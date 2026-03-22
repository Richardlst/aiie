from abc import ABC, abstractmethod

from app.agent.state import State


class BaseNode(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    async def __call__(self, state: State) -> State:
        pass
