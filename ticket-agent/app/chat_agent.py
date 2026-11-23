from datetime import datetime
import json
from typing import Dict, List
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage
from app import agent
from app.llm import get_llm
from app.tools import CHAT_TOOLS, WRITE_TOOLS
from langchain.agents import create_agent

# ====================================================================
# System Prompt
# ====================================================================
# 注意：create_agent 不会对 system_prompt 做 .format()，所以 {} 里的 JSON 可以原样写；
# 所有占位符由我们自己在代码里用 f-string 替换好再传进去。
#
# 【重要】不再有任何 Thought/Action/Action Input/Observation 格式要求 ——
# 有原生 function calling 后，那些文本格式要求是有害的（会诱导模型输出纯文本而不是调工具）
SYSTEM_PROMPT = """你是企业 IT 运维系统的 AI 助手。你可以通过调用工具来查询和操作工单。

    【日期】
    - 今天：{today}（{weekday}）
    - 日期参数可直接传字面量：today / yesterday / week_start / month_start，
      工具内部会自动转成真实日期；也可以直接传 YYYY-MM-DD。

    【工作规则】
    1. 读类工具（list_tickets / get_ticket_detail / query_knowledge / query_history_tickets）可直接调用
    2. 写类工具（create_ticket / update_ticket）在调用前，必须先在回复里向用户说明你要做什么
    3. 工具返回 "error" 时，直接如实告知用户，不要重试或硬扛
    4. 找不到答案就说「我不知道」，不要编造
    5. 知识库检索（query_knowledge / query_history_tickets）只取最相关的 1 条，不要传 top_k 参数
    6. 最终回复用中文，简洁清晰"""

_sessions: Dict[str, List[BaseMessage]] = {}


def _get_history(session_id: str) -> List[BaseMessage]:
    return list(_sessions.get(session_id, []))

def _append_history(session_id: str, msg: BaseMessage):
    if session_id not in _sessions:
        _sessions[session_id] = []
    _sessions[session_id].append(msg)

def _last_ai_text(messages: List[BaseMessage]) -> str:
    for m in reversed(messages):
        if isinstance(m, AIMessage) and not m.tool_calls:
            text = m.content if isinstance(m.content, str) else str(m.content)
            if text.strip():
                return text.strip()
    return "AI 未返回任何有用信息"


def _is_tool_success(content: str) -> bool:
    return "error" not in content and "失败" not in content

def _extract_tool_calls(messages: List[BaseMessage]) -> List[Dict]:
    result_by_call_id: Dict[str, ToolMessage] = {
        m.tool_call_id: m for m in messages
        if isinstance(m, ToolMessage) and getattr(m, 'tool_call_id', None)
    }
    records: List[Dict] = []
    for m in messages:
        if not isinstance(m, AIMessage) or not m.tool_calls:
            continue
        for tc in m.tool_calls:
            tm = result_by_call_id.get(tc.get("id"), "")
            obs = tm.content if tm is not None else ""
            obs = obs if isinstance(obs, str) else str(obs)
            records.append({
                "tool": tc.get("name", ""),
                "args": tc.get("args") or {},
                "result_preview": obs[:200],
                "need_confirm": tc.get("name", "") in WRITE_TOOLS,
                "success": _is_tool_success(obs)
            })
    return records

def _dedupe_tool_calls(records: List[Dict]) -> List[Dict]:
    latest: Dict[tuple, Dict] = {}
    for record in records:
        key = (record['tool'], json.dumps(record.get("args") or {}, sort_keys=True, ensure_ascii=False))
        if key not in latest or record.get("success"):
            latest[key] = record
    return list(latest.values())


def run_chat(session_id:str,message:str):
    history = _get_history(session_id)
    now =datetime.now()

    agent = create_agent(
        model =get_llm(),
        tools=CHAT_TOOLS,
        system_prompt=SYSTEM_PROMPT.format(
            today=now.strftime("%Y-%m-%d"),
            weekday=now.strftime("%A")
        )
    )
    collected: List[BaseMessage] = []
    finished: bool = True
    reply = ""

    try:
        for trunk in agent.stream({"messages": [*history, HumanMessage(content=message)]}, stream_mode="values"):
            collected = trunk.get("messages", [])
    except Exception as err:
        finished = False
        reply = _last_ai_text(collected)


    tool_calls = _dedupe_tool_calls(_extract_tool_calls(collected))

    _append_history(session_id,AIMessage(content=reply))

    return {
        "reply": reply,
        "tool_calls": tool_calls,
        "finished": finished,
        "session_id": session_id,
    }
