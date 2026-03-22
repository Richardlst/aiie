from langgraph.graph import StateGraph, START, END
from app.ws.conversation.connection_manager import ConnectionManager
from app.agent.edges import title_edge
from app.agent.nodes import ChatNode
from app.agent.nodes.base_node import BaseNode
from app.agent.nodes.title_generate_node import TitleGenerateNode

from app.ws.conversation.schemas import (
    WSResponse,
    WSResponseDataProcessing,
    WSResponseType,
)
from app.core.logger import setup_logger

from .state import State

logger = setup_logger("Agent")


class Agent:
    def __init__(
        self,
        chat_node: ChatNode,
        title_generate_node: TitleGenerateNode,
        connection_manager: ConnectionManager,
    ):
        self.__chat_node = chat_node
        self.__title_generate_node = title_generate_node
        self.graph = self.__init_graph()
        self.__connection_manager = connection_manager

    def __init_graph(self):
        graph_builder = StateGraph(State)

        # Add nodes
        graph_builder.add_node(*self.__get_node(self.__chat_node))
        graph_builder.add_node(*self.__get_node(self.__title_generate_node))

        # Add edges
        graph_builder.add_conditional_edges(START, title_edge)
        graph_builder.add_edge(self.__title_generate_node.name, self.__chat_node.name)
        graph_builder.add_edge(self.__chat_node.name, END)

        return graph_builder.compile()

    def __get_node(self, node: BaseNode) -> tuple[str, BaseNode]:
        async def wrapper(state: State):
            logger.info(f"Node {node.name} called")
            await self.__connection_manager.send(
                state["conversation"].id,
                WSResponse(
                    type=WSResponseType.PROCESSING,
                    data=WSResponseDataProcessing(process_name=node.name),
                ),
            )
            result = await node(state)
            logger.info(f"Node {node.name} finished")
            return result

        return (node.name, wrapper)

    def invoke(self, state: State) -> State:
        return self.graph.invoke(state)

    async def ainvoke(self, state: State) -> State:
        return await self.graph.ainvoke(state, config={"run_name": "<Agent>"})
