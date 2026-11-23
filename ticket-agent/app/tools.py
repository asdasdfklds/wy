"""
工具集 —— Agent 通过工具调用访问外部系统
,
- query_knowledge / query_history_tickets：向量库检索（只读）
- list_tickets / get_ticket_detail / create_ticket / update_ticket：工单读写，走 SpringBoot HTTP 接口
- 所有工具返回 JSON 字符串，方便 LLM 解析
- 写操作统一由 SpringBoot 落库（单一写入入口，避免双写 MySQL）
- **不做角色/权限判断**：Agent 一律使用 .env 里的服务账号身份
  （internal_user_id / internal_user_role），权限由后端按令牌里的 role 判断
"""
from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timedelta
from typing import Optional

import requests
from langchain_core.tools import tool
from pydantic import BaseModel, ConfigDict, model_validator

from app.vector_store import get_milvus_store, KNOWLEDGE_MIN_SCORE

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------
# 日期字面量归一化：LLM 传 "today" / "本周" 等字面量时自动转成真实日期
# ----------------------------------------------------------------------
def _normalize_date(s: Optional[str]) -> Optional[str]:
    """
    把 LLM 传的各种日期字面量转成 YYYY-MM-DD
    支持：today / 今天 / yesterday / 昨天 / week_start / 本周一 / month_start / 本月一号
    已经 YYYY-MM-DD 格式的透传
    """
    if not s:
        return s
    s = str(s).strip()
    if not s:
        return s

    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    yesterday = (now - timedelta(days=1)).strftime("%Y-%m-%d")
    week_start = (now - timedelta(days=now.weekday())).strftime("%Y-%m-%d")
    month_start = now.replace(day=1).strftime("%Y-%m-%d")

    mapping = {
        "today": today, "今天": today,
        "yesterday": yesterday, "昨天": yesterday,
        "week_start": week_start, "本周一": week_start, "本周": week_start,
        "month_start": month_start, "本月一号": month_start, "本月1号": month_start, "本月": month_start,
    }
    if s in mapping:
        return mapping[s]
    # 尝试直接当 YYYY-MM-DD 返回
    try:
        datetime.strptime(s, "%Y-%m-%d")
        return s
    except Exception:
        # 无法识别：原样返回，让 SpringBoot 端返回错误便于发现
        logger.warning("无法识别的日期字面量：%s", s)
        return s


# ----------------------------------------------------------------------
# 字面量归一化的公共工具
# ----------------------------------------------------------------------
def _compact(s: str) -> str:
    """
    去掉空格 / 连字符 / 下划线并转小写 —— 别名表的键统一用这个形式存，
    这样 "in progress" / "in_progress" / "In-Progress" 能命中同一条
    """
    return s.replace(" ", "").replace("-", "").replace("_", "").lower()


# ----------------------------------------------------------------------
# 状态字面量归一化：LLM 经常传"已解决 / 待处理"等中文，工具内部转成 PENDING/PROCESSING/RESOLVED/CLOSED
# ----------------------------------------------------------------------
# 合法取值（与后端 sql/init.sql 的 status 列默认值一致）
_STATUS_ENUM = {"PENDING", "PROCESSING", "RESOLVED", "CLOSED"}

# 别名表：键统一是「小写 + 无分隔符」形式，值是标准枚举
_STATUS_ALIAS = {
    # PENDING
    "pending": "PENDING",
    "待处理": "PENDING",
    "未处理": "PENDING",
    "待办": "PENDING",
    "未解决": "PENDING",
    "open": "PENDING",

    # PROCESSING
    "processing": "PROCESSING",
    "inprogress": "PROCESSING",
    "处理中": "PROCESSING",
    "进行中": "PROCESSING",
    "处理": "PROCESSING",

    # RESOLVED
    "resolved": "RESOLVED",
    "已解决": "RESOLVED",
    "已处理": "RESOLVED",
    "解决": "RESOLVED",
    "处理完成": "RESOLVED",
    "完成": "RESOLVED",
    "done": "RESOLVED",
    "fixed": "RESOLVED",

    # CLOSED
    "closed": "CLOSED",
    "已关闭": "CLOSED",
    "关闭": "CLOSED",
    "关单": "CLOSED",
    "close": "CLOSED",
}


# 把 LLM 传的状态字面量归一化成 PENDING/PROCESSING/RESOLVED/CLOSED
def _normalize_status(s: Optional[str]) -> Optional[str]:
    """
    把 LLM 传的状态字面量归一化成 PENDING/PROCESSING/RESOLVED/CLOSED
    - 已是枚举值：原样返回
    - 是中文/英文别名：查表转换
    - 无法识别：返回 None（让调用方报错）
    """
    if s is None:
        return None
    s = str(s).strip()
    if not s:
        return None
    # 大写英文直接匹配
    upper = s.upper()
    if upper in _STATUS_ENUM:
        return upper
    # 别名表（忽略空格/连字符/下划线/大小写）
    return _STATUS_ALIAS.get(_compact(s))


# ----------------------------------------------------------------------
# 故障类型字面量归一化：network / hardware / software / account / unknown
#
# 为什么要映射：LLM 听到用户说中文，往往就把听到的词直接传进来
# （"网络故障" / "电脑坏了" / "登录不上"），而数据库 fault_type 存的是英文码
# （sql/init.sql: 故障类型：network/hardware/software/account）。
# 不映射的后果有两个：
#   1. 查工单时传中文给后端，匹配不到任何行（用户看到"没查到"）
#   2. 建工单时传中文，会被原样写进 fault_type 字段，脏数据
# ----------------------------------------------------------------------

# 合法取值 —— 与 agent.py 的 CLASSIFY_PROMPT、sql/init.sql 的列注释保持一致
_FAULT_TYPE_ENUM = {"network", "hardware", "software", "account", "unknown"}

# 精确别名表：键统一是「小写 + 无分隔符」形式，值是标准英文码
_FAULT_TYPE_ALIAS = {
    # ---------- network ----------
    "network": "network", "networkissue": "network", "networkproblem": "network",
    "网络": "network", "网络故障": "network", "网络问题": "network", "网络异常": "network",
    "网络连接": "network", "网络不通": "network", "网络断了": "network", "断网": "network",
    "无法联网": "network", "无法上网": "network", "上不了网": "network",
    "联网": "network", "上网": "network", "外网": "network", "内网": "network",

    # ---------- hardware ----------
    "hardware": "hardware", "hardwareissue": "hardware", "hardwareproblem": "hardware",
    "硬件": "hardware", "硬件故障": "hardware", "硬件问题": "hardware", "硬件损坏": "hardware",
    "设备": "hardware", "设备故障": "hardware", "设备问题": "hardware",
    "电脑": "hardware", "电脑故障": "hardware", "机器": "hardware", "主机": "hardware",
    "服务器": "hardware", "服务器故障": "hardware",

    # ---------- software ----------
    "software": "software", "softwareissue": "software", "softwareproblem": "software",
    "软件": "software", "软件故障": "software", "软件问题": "software", "软件异常": "software",
    "程序": "software", "程序崩溃": "software", "应用": "software", "应用崩溃": "software",
    "系统": "software", "系统故障": "software", "系统崩溃": "software", "系统问题": "software",

    # ---------- account ----------
    "account": "account", "accountissue": "account", "accountproblem": "account",
    "账号": "account", "帐号": "account", "账号问题": "account", "账号异常": "account",
    "账户": "account", "帐户": "account", "账户问题": "account",
    "权限": "account", "权限问题": "account", "权限不足": "account",
    "密码": "account", "密码错误": "account", "密码问题": "account", "密码忘记": "account",
    "登录": "account", "登录失败": "account", "登录问题": "account", "无法登录": "account",
    "登陆": "account", "登陆失败": "account", "登不上": "account",

    # ---------- unknown ----------
    "unknown": "unknown", "未知": "unknown", "未知类型": "unknown", "不确定": "unknown",
    "其他": "unknown", "其它": "unknown",
}

# 关键词兜底：LLM 的中文表述千变万化（"网络连接不上"/"账号权限不足"…），
# 精确表覆盖不到时按关键词打分 —— 关键词越长越具体，权重就越高；
# 同分时按 _FAULT_TYPE_PRIORITY 的顺序取靠前的那个 优先级。
_FAULT_TYPE_PRIORITY = ("network", "account", "hardware", "software", "unknown")

_FAULT_TYPE_KEYWORDS = {
    "network": ("网络", "断网", "联网", "上网", "网线", "宽带", "路由", "网卡",
                "vpn", "dns", "域名", "端口", "丢包", "ping", "外网", "内网"),
    "account": ("账号", "帐号", "账户", "帐户", "权限", "密码", "登录", "登陆",
                "鉴权", "认证", "授权", "单点登录", "被锁", "锁定", "登不上"),
    "hardware": ("硬件", "主板", "内存", "硬盘", "固态", "显示器", "屏幕", "键盘",
                 "鼠标", "电源", "电池", "蓝屏", "死机", "黑屏", "机箱", "cpu",
                 "显卡", "风扇", "设备", "机器", "服务器", "电脑", "笔记本",
                 "打印机", "投影仪"),
    "software": ("软件", "系统", "程序", "应用", "崩溃", "闪退", "卡死", "报错",
                 "异常", "bug", "驱动", "浏览器", "装不上", "打不开", "无法安装",
                 "补丁", "脚本", "版本"),
    "unknown": ("未知", "不确定", "其他", "其它"),
}


# 把 LLM 传的故障类型归一化成 network/hardware/software/account/unknown
def _normalize_fault_type(s: Optional[str]) -> Optional[str]:
    """
    把 LLM 传的故障类型归一化成 network/hardware/software/account/unknown
    - 已是枚举值：原样返回
    - 中文/英文别名：精确表命中；命中不了再用关键词兜底
    - 无法识别：返回 None（让调用方报错，避免把中文原样写进 fault_type）
    """
    if s is None:
        return None
    s = str(s).strip()
    if not s:
        return None
    # 1) 已经是标准值
    low = s.lower()
    if low in _FAULT_TYPE_ENUM:
        return low
    # 2) 精确别名表
    text = _compact(s)
    hit = _FAULT_TYPE_ALIAS.get(text)
    if hit:
        return hit
    # 3) 关键词兜底
    best, best_score = None, 0
    for cat in _FAULT_TYPE_PRIORITY:
        score = sum(len(kw) for kw in _FAULT_TYPE_KEYWORDS[cat] if kw in text)
        if score > best_score:
            best, best_score = cat, score
    return best


# ----------------------------------------------------------------------
# 工单工具的入参 Schema：把模型常写的 id / ticketId 归一化成 ticket_id
#
# 为什么需要：@tool 自动生成的 schema 没设 extra，pydantic v2 默认 'ignore'
# → 模型传 id 时会被静默丢弃，ticket_id 报 missing，工具根本没被调用。
# before 校验器在字段校验之前改写键名，比覆写 BaseTool.run() 简单得多。
# ----------------------------------------------------------------------
class _TicketArgs(BaseModel):
    """工单类工具的入参基类"""

    model_config = ConfigDict(extra="ignore")

    @model_validator(mode="before")
    @classmethod
    def _alias_ticket_id(cls, data):
        if isinstance(data, dict) and "ticket_id" not in data:
            for alias in ("id", "ticketId"):
                if alias in data:
                    data = {**data, "ticket_id": data.pop(alias)}
                    break
        return data


class _DetailArgs(_TicketArgs):
    ticket_id: int


class _UpdateArgs(_TicketArgs):
    ticket_id: int
    status: Optional[str] = None
    resolution: Optional[str] = None


# ----------------------------------------------------------------------
# 调 SpringBoot 后端用于保存工单
# ----------------------------------------------------------------------

def _spring_headers() -> dict:
    """内部调用时携带的系统身份令牌，让后端信任 Agent 的请求"""
    return {
        "Authorization": os.getenv("AGENT_TOKEN"),
        "Content-Type": "application/json",
    }


def _log_auth_error(resp) -> None:
    """
    401 统一提示：绝大多数情况是两边密钥不一致

    教学要点：
    - Agent 用 settings.jwt_secret（.env 的 JWT_SECRET）签令牌
    - 后端用 sa-token.jwt-secret-key（application.yml 的 ${JWT_SECRET:...}）验令牌
    - 两边必须完全一致，否则后端一律 401
    """
    logger.error(
        "SpringBoot 返回 401：多半是 Sa-Token 密钥不一致。\n"
        "  · Agent 侧读 settings.jwt_secret（.env 的 JWT_SECRET）\n"
        "  · 后端侧读 sa-token.jwt-secret-key（application.yml 的 ${JWT_SECRET:...}）\n"
        "  两边必须完全一致。响应体：%s", resp.text[:200])


def _call_spring(method: str, path: str, *, json_body=None, params=None, timeout=10):
    """通用 SpringBoot 调用封装"""
    url = os.getenv("SPRING_BOOT_BASE_URL") + path
    try:
        resp = requests.request(
            method, url,
            headers=_spring_headers(),
            json=json_body,
            params=params,
            timeout=timeout,
        )
        if resp.status_code >= 400:
            if resp.status_code == 401:
                _log_auth_error(resp)
            else:
                logger.warning("SpringBoot 返回 %s: %s", resp.status_code, resp.text[:200])
            return {"error": f"HTTP {resp.status_code}", "body": resp.text[:300]}
        return resp.json()
    except Exception as e:
        logger.exception("调 SpringBoot 失败：%s %s", method, url)
        return {"error": str(e)}


# ----------------------------------------------------------------------
# 向量库检索工具（只读）
# ----------------------------------------------------------------------
#@tool将python转化成lonagchain工具
@tool
def query_knowledge(query: str, top_k: int = 1) -> str:
    """
    在运维知识库中检索与 query 语义最相关的内容。
    相似度低于阈值（KNOWLEDGE_MIN_SCORE）的结果视为没命中，不会返回。
    """
    store = get_milvus_store(os.getenv("MILVUS_KNOWLEDGE"))
    results = store.search(query, top_k=top_k, min_score=KNOWLEDGE_MIN_SCORE)
    if not results:
        return "知识库没有找到相关内容。"
    # 工具返回值最终要拼进 prompt 给 LLM 看。返回字符串（带换行的列表文本）比返回结构化数据更省 token、也更容易被 LLM 正确理解。
    lines = [f"- [相似度 {r['score']}] {r['title']}：{r['content']}" for r in results]
    return "\n".join(lines)


@tool
def query_history_tickets(query: str, top_k: int = 3) -> str:
    """在历史工单向量库中检索与 query 语义相似的工单。"""
    store = get_milvus_store(os.getenv("MILVUS_TICKET"))
    results = store.search(query, top_k=top_k)
    if not results:
        return "没有找到相似的历史工单。"
    # 正文截取80个字符 信息太少 LLM 答不出细节
    lines = [f"- [相似度 {r['score']}] {r['title']}：{r['content'][:80]}" for r in results]
    return "\n".join(lines)


# ----------------------------------------------------------------------
# 工单工具
# ----------------------------------------------------------------------
@tool
def list_tickets(
        status: Optional[str] = None,
        fault_type: Optional[str] = None,
        submitter_id: Optional[int] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        limit: int = 20,
) -> str:
    """
    列出工单，支持按状态、故障类型、提交人、日期范围过滤。

    fault_type 接受（工具内部归一化为 network/hardware/software/account）：
      - 英文枚举：network / hardware / software / account
      - 中文：网络 / 硬件 / 软件 / 账号（也兼容"网络故障""登录不上"这类说法）
    status 接受（工具内部归一化为 PENDING/PROCESSING/RESOLVED/CLOSED）：
      - 英文枚举：PENDING / PROCESSING / RESOLVED / CLOSED
      - 中文：待处理 / 处理中 / 已解决 / 已关闭

    日期参数格式：YYYY-MM-DD（如 "2026-10-19"），也可以传 today / week_start 等字面量，工具会自动转换。
    """
    # 归一化 status：LLM 经常传"已解决 / 处理中"等中文，后端只认大写枚举
    norm_status = _normalize_status(status)
    if status and not norm_status:
        return json.dumps({
            "error": f"无法识别的状态值：{status}",
            "hint": "可用：PENDING/PROCESSING/RESOLVED/CLOSED（或中文：待处理/处理中/已解决/已关闭）",
        }, ensure_ascii=False)

    # 归一化 fault_type：LLM 经常传"网络故障 / 权限不足"等中文，
    # 后端 fault_type 字段存的是英文码，不转就查不到任何行
    norm_fault = _normalize_fault_type(fault_type)
    if fault_type and not norm_fault:
        return json.dumps({
            "error": f"无法识别的故障类型：{fault_type}",
            "hint": "可用：network/hardware/software/account（或中文：网络/硬件/软件/账号）",
        }, ensure_ascii=False)

    # 关键：把 LLM 传的日期字面量（"today" / "本周" 等）转成真实 YYYY-MM-DD
    date_from_norm = _normalize_date(date_from)
    date_to_norm = _normalize_date(date_to)
    logger.debug("日期归一化: dateFrom=%s dateTo=%s", date_from_norm, date_to_norm)

    params = {"page": 1, "size": max(1, min(limit, 50))}
    if norm_status:   params["status"] = norm_status
    if norm_fault:    params["faultType"] = norm_fault
    if submitter_id:  params["submitterId"] = submitter_id
    if date_from_norm: params["dateFrom"] = date_from_norm
    if date_to_norm:   params["dateTo"] = date_to_norm

    result = _call_spring("GET", "/api/ticket", params=params)
    if "error" in result:
        return json.dumps(result, ensure_ascii=False)

    items = (result.get("data") or {}).get("list") or []
    slim = [{
        "id": t.get("id"),
        "title": t.get("title"),
        "status": t.get("status"),
        "faultType": t.get("faultType"),
        "submitterId": t.get("submitterId"),
        "createTime": t.get("createTime"),
    } for t in items]
    return json.dumps({"count": len(slim), "list": slim}, ensure_ascii=False)


@tool(args_schema=_DetailArgs)
def get_ticket_detail(ticket_id: int) -> str:
    """按 ID 查询工单详情。工单 ID 就是工单编号。"""
    result = _call_spring("GET", f"/api/ticket/{ticket_id}")
    if "error" in result:
        return json.dumps(result, ensure_ascii=False)

    payload = result.get("data")
    if not payload:
        return json.dumps({"error": "工单不存在"}, ensure_ascii=False)
    return json.dumps(payload, ensure_ascii=False)


@tool
def create_ticket(
        title: str,
        description: str,
        fault_type: Optional[str] = None,
        submitter_id: int = 0,
) -> str:
    """创建一条新工单。后端会自动调用 AI 分析并写入向量库。

    fault_type 接受（工具内部归一化为 network/hardware/software/account）：
      - 英文枚举：network / hardware / software / account
      - 中文：网络 / 硬件 / 软件 / 账号
    识别不出来就别传，后端会让 AI 自动判定。
    """
    if not title or not description:
        return json.dumps({"error": "title 和 description 不能为空"}, ensure_ascii=False)

    # 归一化 fault_type：LLM 常传中文（"网络故障"/"登录不上"），
    # 不转的话中文会被原样写进 fault_type 字段，之后按类型查询就再也查不到了
    norm_fault = _normalize_fault_type(fault_type)
    if fault_type and not norm_fault:
        return json.dumps({
            "error": f"无法识别的故障类型：{fault_type}",
            "hint": "可用：network/hardware/software/account（或中文：网络/硬件/软件/账号）；"
                    "不传则由后端 AI 自动识别",
        }, ensure_ascii=False)

    body = {"title": title, "description": description}
    if norm_fault:
        body["faultType"] = norm_fault

    headers = _spring_headers()
    try:
        url = os.getenv("SPRING_BOOT_BASE_URL") + "/api/ticket"
        resp = requests.post(url, headers=headers, json=body, timeout=30)
        if resp.status_code >= 400:
            if resp.status_code == 401:
                # 这里没走 _call_spring，所以要自己补一条能照着改的提示
                _log_auth_error(resp)
            return json.dumps({"error": f"HTTP {resp.status_code}", "body": resp.text[:200]},
                              ensure_ascii=False)
        data = resp.json().get("data") or {}
        return json.dumps({
            "id": data.get("id"),
            "title": data.get("title"),
            "status": data.get("status"),
            "faultType": data.get("faultType"),
        }, ensure_ascii=False)
    except Exception as e:
        logger.exception("create_ticket 失败")
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@tool(args_schema=_UpdateArgs)
def update_ticket(
        ticket_id: int,
        status: Optional[str] = None,
        resolution: Optional[str] = None,
) -> str:
    """更新工单的状态或处理结果。

    ticket_id 是工单编号。

    status 接受（工具内部归一化为 PENDING/PROCESSING/RESOLVED/CLOSED）：
      - 英文枚举：PENDING / PROCESSING / RESOLVED / CLOSED
      - 中文：待处理 / 处理中 / 已解决 / 已关闭
      - 别名：解决/完成/done/fixed/关闭/close...
    """
    # 归一化 status：LLM 经常传"已解决 / 处理中"等中文
    norm_status = _normalize_status(status)
    if status and not norm_status:
        return json.dumps({
            "error": f"无法识别的状态值：{status}",
            "hint": "可用：PENDING/PROCESSING/RESOLVED/CLOSED（或中文：待处理/处理中/已解决/已关闭）",
        }, ensure_ascii=False)

    body = {}
    if norm_status: body["status"] = norm_status
    if resolution:  body["resolution"] = resolution
    if not body:
        return json.dumps({"error": "至少要提供 status 或 resolution 之一"}, ensure_ascii=False)

    result = _call_spring("PUT", f"/api/ticket/{ticket_id}", json_body=body, timeout=15)
    if "error" in result:
        return json.dumps(result, ensure_ascii=False)

    payload = result.get("data") or {}
    return json.dumps({
        "id": payload.get("id"),
        "status": payload.get("status"),
        "resolution": payload.get("resolution"),
    }, ensure_ascii=False)


CHAT_TOOLS = [
    list_tickets,
    get_ticket_detail,
    create_ticket,
    update_ticket,
    query_knowledge,
    query_history_tickets,
]
# 写类工具：前端据此弹确认框
WRITE_TOOLS = {"create_ticket", "update_ticket"}
