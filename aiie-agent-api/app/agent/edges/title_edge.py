from app.agent.nodes.chat_node import ChatNode
from app.agent.nodes.title_generate_node import TitleGenerateNode
from app.agent.state import State


def title_edge(state: State):
    if state["conversation"].name is None:
        return TitleGenerateNode.name
    return ChatNode.name
