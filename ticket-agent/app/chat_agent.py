from app.llm import get_llm
from langchain.agents import create_agent



def run_chat(session_id:str,message:str):

    agent = create_agent(
        model =get_llm
    )