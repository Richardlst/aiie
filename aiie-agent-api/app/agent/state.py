from typing import List, Annotated, TypedDict
from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages
from app.api.conversation.models import Conversation


class State(TypedDict):
    messages: Annotated[List[AnyMessage], add_messages]

    conversation: Conversation
