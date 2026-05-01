from langchain_core.messages import AIMessage, ToolMessage

from .txt2img import text2img
from .img2img import img2img
from .inpaint import inpaint
from .segment import segment
from .expand import expand
from .sr import super_resulution
from .gfpgan import gfpgan
tools = [text2img, img2img, inpaint, segment, expand, super_resulution, gfpgan]
tools_dict = {tool.name: tool for tool in tools}


async def tool_run(message: AIMessage) -> list[ToolMessage]:
    tool_calls = message.tool_calls
    tool_messages = []
    for tool_call in tool_calls:
        tool = tools_dict[tool_call["name"]]
        result = await tool.ainvoke(tool_call["args"])
        tool_messages.append(
            ToolMessage(content=str(result), tool_call_id=tool_call["id"])
        )
    return tool_messages


__all__ = ["tool_run", "tools", "tools_dict"]
