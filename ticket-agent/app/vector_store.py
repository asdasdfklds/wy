import logging
import os
import threading
import time

from pymilvus import MilvusClient, DataType

from app.llm import get_embedding

logger = logging.getLogger(__name__)

# 集合必须具备的字段：字段名 -> (数据类型, 建字段参数)
# item_id 是业务主键（知识库 id / 工单 id）。老集合里没有这个字段，
# 检索时 Milvus 会直接报 `field item_id not exist`，所以启动时必须校验结构。
REQUIRED_FIELDS = {
    "item_id": (DataType.INT64, {}),
    "title": (DataType.VARCHAR, {"max_length": 500}),
    "content": (DataType.VARCHAR, {"max_length": 5000}),
    "category": (DataType.VARCHAR, {"max_length": 64}),
}
PRIMARY_FIELD = "id"
VECTOR_FIELD = "vector"
VECTOR_DIM = 384

# 迁移老集合时一次性搬运的最大行数，超过这个量说明数据太大，不适合在启动时自动搬
MIGRATE_LIMIT = 10000


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, default))
    except (TypeError, ValueError):
        return default


# 知识库检索的相似度下限（COSINE 索引，分数越高越像）。
# 低于这个分数认为没命中，不返回给调用方；可用环境变量 KNOWLEDGE_MIN_SCORE 调整。
KNOWLEDGE_MIN_SCORE = _env_float("KNOWLEDGE_MIN_SCORE", 0.7)

_store_cache = {}
_cache_lock = threading.Lock()


class MilvusStore:
    def __init__(self, collection_name: str):
        self.collection_name = collection_name
        self._connect()

    # ------------------------------------------------------------------
    # 连接与集合结构
    # ------------------------------------------------------------------
    def _connect(self):
        host = os.getenv("MILVUS_HOST")
        port = os.getenv("MILVUS_PORT")
        if not host or not port:
            raise RuntimeError("缺少 MILVUS_HOST / MILVUS_PORT 环境变量，无法连接 Milvus")
        self.client = MilvusClient(uri=f"http://{host}:{port}")
        self._embedding = get_embedding()
        self._ensure_schema()

    def _ensure_schema(self):
        """集合不存在就建；已存在但字段不全（老集合）就迁移。

        早期版本的 knowledge 集合只有 id/title/content/category/vector，没有 item_id，
        而检索按 item_id 过滤/取字段，必然报 `field item_id not exist`。
        """
        if not self.client.has_collection(self.collection_name):
            self._create_collection()
        else:
            existing = {f["name"] for f in self.client.describe_collection(self.collection_name)["fields"]}
            missing = [name for name in REQUIRED_FIELDS if name not in existing]
            if missing:
                logger.warning("集合 %s 缺少字段 %s，开始迁移", self.collection_name, missing)
                self._migrate(missing)
            else:
                self._load()
        self._fields = [
            name for name in REQUIRED_FIELDS
            if name in {f["name"] for f in self.client.describe_collection(self.collection_name)["fields"]}
        ]

    def _create_collection(self):
        schema = self.client.create_schema(auto_id=True)
        schema.add_field(PRIMARY_FIELD, DataType.INT64, is_primary=True)
        for name, (dtype, kwargs) in REQUIRED_FIELDS.items():
            schema.add_field(name, dtype, **kwargs)
        schema.add_field(VECTOR_FIELD, DataType.FLOAT_VECTOR, dim=VECTOR_DIM)

        index_params = self.client.prepare_index_params()
        index_params.add_index(field_name=VECTOR_FIELD)
        self.client.create_collection(
            collection_name=self.collection_name, schema=schema, index_params=index_params
        )
        self._load()
        logger.info("已创建集合 %s", self.collection_name)

    def _load(self):
        """新建/迁移后的集合要显式 load，否则刚写进去的数据 query 读不到。"""
        self.client.load_collection(self.collection_name)

    def _migrate(self, missing_fields):
        """把老集合迁移成当前 schema。

        做法：老集合改名备份 -> 用新 schema 建同名集合 -> 把数据搬过去。
        老集合的主键 id 就是业务 id，搬过去后写进 item_id，
        这样按 item_id 过滤的删除/更新接口对老数据依然有效。
        """
        schema = self.client.describe_collection(self.collection_name)
        existing = {f["name"]: f for f in schema["fields"]}
        if VECTOR_FIELD not in existing:
            raise RuntimeError(
                "集合 {} 没有向量字段，无法自动迁移，请手工重建".format(self.collection_name)
            )
        dim = int(existing[VECTOR_FIELD].get("params", {}).get("dim", VECTOR_DIM))
        if dim != VECTOR_DIM:
            raise RuntimeError(
                "集合 {} 的向量维度是 {}，与当前嵌入模型({})不一致，请手工重建".format(
                    self.collection_name, dim, VECTOR_DIM
                )
            )

        want = [f for f in (PRIMARY_FIELD, "title", "content", "category", VECTOR_FIELD) if f in existing]
        old_rows = self.client.query(
            collection_name=self.collection_name, filter="", output_fields=want, limit=MIGRATE_LIMIT + 1
        )
        if len(old_rows) > MIGRATE_LIMIT:
            raise RuntimeError(
                "集合 {} 数据量超过 {} 行，请手工迁移，不要在启动时自动搬运".format(
                    self.collection_name, MIGRATE_LIMIT
                )
            )

        backup = "{}_legacy_{}".format(self.collection_name, time.strftime("%Y%m%d%H%M%S"))
        self.client.rename_collection(old_name=self.collection_name, new_name=backup)
        try:
            self._create_collection()
            data = []
            for row in old_rows:
                item_id = row.get("item_id")
                if item_id is None:
                    item_id = row.get(PRIMARY_FIELD)
                data.append({
                    "item_id": item_id,
                    "title": row.get("title") or "",
                    "content": row.get("content") or "",
                    "category": row.get("category") or "",
                    VECTOR_FIELD: row.get(VECTOR_FIELD),
                })
            if data:
                self.client.insert(collection_name=self.collection_name, data=data)
                self.client.flush(self.collection_name)
        except Exception:
            # 迁移失败就把备份改回原名，宁可报错也不能把老数据丢在半路
            self.client.rename_collection(old_name=backup, new_name=self.collection_name)
            raise
        logger.info(
            "集合 %s 迁移完成（补齐字段 %s，%d 行数据），老集合已备份为 %s",
            self.collection_name, missing_fields, len(data), backup,
        )

    # ------------------------------------------------------------------
    # 读写
    # ------------------------------------------------------------------
    def insert(self, item_id: int, title: str, content: str, category: str):
        """写入一条记录。同一个 item_id 只保留最新一条，避免重复分析同一工单产生重复数据。"""
        vec = self._embedding.embed_query("{}\n{}".format(title, content))
        self._save(item_id, title, content, category, vec)

    def _save(self, item_id: int, title: str, content: str, category: str, vec):
        self.delete(item_id)
        self.client.insert(
            collection_name=self.collection_name,
            data=[
                {
                    "item_id": item_id,
                    "title": title,
                    "content": content,
                    "category": category,
                    VECTOR_FIELD: vec
                }
            ]
        )
        # Milvus 写入是异步的，flush 一下保证紧接着的检索能查到这条数据
        self.client.flush(self.collection_name)

    def search(self, query: str, top_k: int, min_score: float = 0.3):
        """向量检索，返回 [{item_id, title, content, category, score}]。

        min_score：相似度下限。索引用的是 COSINE，分数越高越像，
        低于这个分数的视为没命中，直接丢掉不返回。

        两个容易踩的坑：
        1. pymilvus 的 MilvusClient.search 只认 limit 参数，写 top_k 会被静默忽略（一直按默认 10 条返回）；
        2. 标量字段在 hit["entity"] 里、distance 在 hit 顶层，直接 hit.get("title") 拿到的全是 None。
        """
        """"将查询操作转换为向量"""
        vec = self._embedding.embed_query(query)
        results = self.client.search(
            ##去哪个集合查找
            collection_name=self.collection_name,
            ##拿什么去找
            data=[vec],
            #跟哪一列比较。
            anns_field=VECTOR_FIELD,
            limit=top_k,
            #每条记录带回哪些字段
            output_fields=self._fields,
        )
        print(results)
        out_result = []
        for hits in results:
            for hit in hits:
                score = float(hit.get("distance", 0.0))
                if score < min_score:
                    continue
                entity = hit.get("entity") or {}
                out_result.append({
                    "item_id": entity.get("item_id", hit.get(PRIMARY_FIELD)),
                    "title": entity.get("title") or "",
                    "content": entity.get("content") or "",
                    "category": entity.get("category") or "",
                    "score": score
                })
        return out_result

    def delete(self, item_id: int):
        self.client.delete(
            collection_name=self.collection_name,
            filter="item_id == {}".format(int(item_id))
        )

    def update(self, item_id: int, title: str, description: str, fault_type: str, resolution: str):
        vec = self._embedding.embed_query("{}\n{}\n{}".format(title, description, resolution))
        self._save(item_id, title, description + "，处理结果:" + resolution, fault_type, vec)


def get_milvus_store(collection_name: str) -> MilvusStore:
    """按集合名复用 Store：省掉每个请求都重新连 Milvus + 重新加载嵌入模型（加载一次要好几秒）。"""
    if not collection_name:
        raise RuntimeError("集合名为空，请检查 MILVUS_KNOWLEDGE / MILVUS_TICKET 环境变量")
    with _cache_lock:
        store = _store_cache.get(collection_name)
        if store is None:
            store = MilvusStore(collection_name)
            _store_cache[collection_name] = store
        return store
