from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.ws.conversation.connection_manager import ConnectionManager
from app.agent.state import State

from .base_node import BaseNode


class TitleGenerateNode(BaseNode):
    name = "title_generate"

    def __init__(
        self,
        connection_manager: ConnectionManager,
        chat_model: BaseChatModel
    ):
        self.chat_model = chat_model

    async def __call__(self, state: State) -> State:
        prompt_template = ChatPromptTemplate.from_template(
            '''
            You are a helpful assistant that generates a title for a conversation base on the first message.
            Rules:
            - THE TITLE SHOULD BE A SHORT AND CONCISE DESCRIPTION OF THE CONVERSATION.
            - THE TITLE SHOULD BE IN ENGLISH.
            - THE TITLE SHOULD BE NO MORE THAN 255 CHARACTERS.
            - YOU SHOULD RETURN ONLY THE TITLE, NOTHING ELSE.
            
            Example:
            - "This is the title should be returned"
            - "Danang - one of the most beautiful cities in Vietnam"

            The first message is:
            """{first_message}"""
            '''
        )

        chain = prompt_template | self.chat_model | StrOutputParser()
        response = await chain.ainvoke(
            {"first_message": state["messages"][0].content},
            config={"run_name": "<TitleGenerateNode>"},
        )
        conversation = state["conversation"].model_copy()
        conversation.name = response
        return {"conversation": conversation}
