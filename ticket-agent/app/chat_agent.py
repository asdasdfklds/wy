from app.llm import get_llm
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

def run_chat(session_id:str,message:str):

    agent = create_agent(
        model =get_llm().
        tools=CHAT_TOOLS,
        system_prompt=
    )