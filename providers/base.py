from abc import ABC, abstractmethod
from typing import AsyncGenerator, Optional


class BaseProvider(ABC):
    def __init__(self, config: dict):
        self.name = "base"
        self.config = config
        self.api_key = config.get("api_key", "")
        self.base_url = ""
        self.supports_thinking = False
        self.supports_tool_calling = False
        self.default_model = ""

    @abstractmethod
    async def validate(self) -> bool:
        pass

    @abstractmethod
    async def stream(self, messages, tools=None, model=None, temperature=0.7, max_tokens=8000, thinking="off") -> AsyncGenerator:
        pass

    @abstractmethod
    async def list_models(self) -> list:
        pass

    def get_recommended_models(self) -> list:
        return []

    def get_system_prompt_appendix(self) -> str:
        return ""
