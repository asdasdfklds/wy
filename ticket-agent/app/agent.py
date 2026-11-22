import json
import os
import re

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.llm import get_llm


SYSTEM_PROMPT = """你是企业 IT 运维智能助手，请根据用户的故障描述和检索到的参考资料给出专业的初步排查建议。
    要求：
    1. 严格基于检索到的资料回答，不要凭空捏造命令
    2. 输出结构化 JSON，不要包含 Markdown 代码块    
    返回 JSON 格式：
    {
      "fault_type": "network | hardware | software | account | unknown 之一",
      "need _human": true 或 false,   // 是否需要人工介入
      "suggestion": "<完整的初步排查建议文本，最多 400 字>"
    }
    """

CLASSIFY_PROMPT = """你是故障分类助手。请把下面的工单描述归类为：
    network（网络）/ hardware（硬件）/ software（软件）/ account（账号权限）/ unknown
    只允许输出上述 5 个单词之一，不要任何解释。
    工单标题：{title}
    工单描述：{description}
    """


def _safe_json(text: str):
    """
    从 LLM 输出中抠出 JSON
    返回 (parsed_dict, used_fallback)；used_fallback=True 表示解析失败、走兜底
    """
    text = text.strip()
    # 移除可能的代码块
    text = re.sub(r"^```(json)?", "", text).rstrip("`").strip()
    try:
        return json.loads(text), False
    except Exception:
        # 抓大括号
        m = re.search(r"\{.*\}", text, re.S)
        if m:
            try:
                return json.loads(m.group(0)), False
            except Exception:
                pass
    return {"fault_type": "unknown", "need_human": True, "suggestion": text[:400]}, True


# 大模型分析故障类型
def classify_fault(llm: ChatOpenAI, title: str, description: str):
    fault_prompt = CLASSIFY_PROMPT.format(title=title, description=description)
    response = llm.invoke([HumanMessage(content=fault_prompt)])
    word = response.content.strip().lower()
    if word in {"network", "hardware", "software", "account", "unknown"}:
        return word
    return "unknown"


def run_agent(title, description, fault_type):
    """分析工单，返回 (LLM 结论, 相似工单, 相似知识)。

    检索结果一并返回，路由层直接复用，不要再查一遍（每次检索都要算一次嵌入）。
    """
    llm = get_llm()
    #os.getenv(...) 读取配置里的集合名，`get_milvus_store(...)` 拿到操作该集合的对象。`knowledge_store` 用来查知识库，`ticket_store` 用来查历史工单
    knowledge_store = get_milvus_store(os.getenv("MILVUS_KNOWLEDGE"))
    ticket_store = get_milvus_store(os.getenv("MILVUS_TICKET"))
    if fault_type not in ["network", "hardware", "software", "account"]:
        fault_type = classify_fault(llm, title, description)
    full_query = f"{title}\n{description}"
    # 知识库按相似度阈值过滤，低于阈值的直接不返回（没有就是没有，别硬凑）
    knowledge_result = knowledge_store.search(full_query, 1, min_score=KNOWLEDGE_MIN_SCORE)
    #最多取 3 条相似工单，最低分是 0.75。所以实际查到的条数可能更少。
    ticket_result = ticket_store.search(full_query, 3, 0.75)
    knowledge_line = "\n".join(
        f"- 相似度{r['score']} {r['title']}:{r['content']}" for r in knowledge_result
    ) or "（没有检索到相似度足够高的知识库内容）"
    ticket_line = "\n".join(
        f"- 相似度{r['score']} {r['title']}:{r['content']}" for r in ticket_result
    )
    user_prompt = f"""
        标题:{title},
        描述:{description},
        故障类型:{fault_type}
        【知识库检索结果】
        {knowledge_line}  
        【工单检索结果】
        {ticket_line}
        请按 JSON 格式输出：故障类型、初步排查建议、是否需要人工介入     
        """
    try:
        resp = llm.invoke(
            [
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=user_prompt)
            ]
        )
    except Exception as e:
        parsed = {
            "fault_type": fault_type,
            "need_human": True,
            "suggestion": "AI 暂不可用，请人工处理"
        }
    else:
        parsed, used = _safe_json(resp.content)

    return parsed, ticket_result, knowledge_result

