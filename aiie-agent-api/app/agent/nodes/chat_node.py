import uuid
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition

from app.core.logger import setup_logger
from app.ws.conversation.connection_manager import ConnectionManager
from app.agent.state import State
from app.agent.tools import tools
from app.ws.conversation.schemas import (
    WSResponse,
    WSResponseType,
    WSResponseDataProcessing,
)

from .base_node import BaseNode

logger = setup_logger("ChatNode")


class ChatNode(BaseNode):
    name = "chat"

    def __init__(
        self,
        connection_manager: ConnectionManager,
        chat_model: BaseChatModel
    ):
        self.chat_model = chat_model.bind_tools(tools=tools)
        self.connection_manager = connection_manager
        self.graph = self.__init_graph()

    async def __send_ws_response(
        self,
        connection_manager: ConnectionManager,
        conversation_id: uuid.UUID,
        process_name: str,
    ):
        await connection_manager.send(
            conversation_id,
            WSResponse(
                type=WSResponseType.PROCESSING,
                data=WSResponseDataProcessing(process_name=process_name),
            ),
        )

    def __init_graph(self):
        graph_builder = StateGraph(State)

        async def chatbot_node(state: State):
            await self.__send_ws_response(
                self.connection_manager, state["conversation"].id, "llm"
            )
            logger.info("LLM called")
            response = await self.chat_model.ainvoke(state["messages"])
            if response.tool_calls:
                logger.info(
                    f"Tool {[tool['name'] for tool in response.tool_calls]} called"
                )
                await self.__send_ws_response(
                    self.connection_manager, state["conversation"].id, "tool"
                )
            return {"messages": [response]}

        tool_node = ToolNode(tools=tools)

        graph_builder.add_node("chatbot", chatbot_node)
        graph_builder.add_node("tools", tool_node)

        graph_builder.add_edge(START, "chatbot")
        graph_builder.add_conditional_edges(
            "chatbot",
            tools_condition,
            {"tools": "tools", END: END},
        )
        graph_builder.add_edge("tools", "chatbot")

        return graph_builder.compile()

    def __get_system_message(self) -> HumanMessage:
        return SystemMessage(
            content="""You are an intelligent AI assistant specializing in visual creation and manipulation. Your primary capabilities revolve around image-related tasks, though you can also answer general questions.
Guidelines:
- When a tool return an image_url, you MUST add it to the next message with format: ![random_name](url) to display the image.
- When you call a tool, you MUST fill in the prompt and negative prompt in a detailed and complete manner.
- Always format responses in Markdown for improved readability.
- Ensure all image generation prompts are translated to English if the user request is in another language.
- For general questions, provide concise, accurate responses without unnecessary tool invocation.
- When uncertain about visual preferences, ask clarifying questions before generating images.
"""
        )

    async def __call__(self, state: State) -> State:
        messages = [self.__get_system_message()] + state["messages"]
        new_state: State = await self.graph.ainvoke(
            {"messages": messages, "conversation": state["conversation"]},
            config={"run_name": "<ChatNode>"},
        )
        response = new_state["messages"][-1]
        return {"messages": [response]}
