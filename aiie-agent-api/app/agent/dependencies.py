from typing import Annotated
from fastapi import Depends
from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI

from app.agent.agent import Agent
from app.agent.nodes.chat_node import ChatNode
from app.agent.nodes.title_generate_node import TitleGenerateNode
from app.core.settings import settings
from app.ws.conversation.dependencies import ConnectionManagerDep
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama 
import os

def get_chat_model():
    # Sử dụng llama3.1 để có khả năng gọi Tool (gfpgan, super_resolution...)
    return ChatOllama(
        model="llama3.1", 
        temperature=0,      # Để 0 để AI chọn tool chính xác hơn, ít "sáng tạo" linh tinh
        base_url="http://localhost:11434"
    )


def get_chat_node(
    connection_manager: ConnectionManagerDep,
    chat_model: BaseChatModel = Depends(get_chat_model),
):
    return ChatNode(connection_manager=connection_manager, chat_model=chat_model)


def get_title_generate_node(
    connection_manager: ConnectionManagerDep,
    chat_model: BaseChatModel = Depends(get_chat_model),
):
    return TitleGenerateNode(connection_manager=connection_manager, chat_model=chat_model)


def get_agent(
    connection_manager: ConnectionManagerDep,
    chat_node: ChatNode = Depends(get_chat_node),
    title_generate_node: TitleGenerateNode = Depends(get_title_generate_node),
):
    return Agent(
        chat_node=chat_node,
        title_generate_node=title_generate_node,
        connection_manager=connection_manager,
    )


AgentDep = Annotated[Agent, Depends(get_agent)]
