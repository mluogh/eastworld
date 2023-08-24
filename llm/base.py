from abc import abstractmethod
from typing import Dict, List, Optional, Union

from schema import ActionCompletion, Message


class LLMBase:
    @abstractmethod
    async def completion(
        self, messages: List[Message], functions: List[Dict[str, str]]
    ) -> Union[Message, ActionCompletion]:
        """Returns a chat or action completion from the LLM."""

    @abstractmethod
    async def chat_completion(
        self,
        messages: List[Message],
    ) -> Message:
        """Returns a chat completion from the LLM."""

    @abstractmethod
    async def action_completion(
        self, messages: List[Message], functions: List[Dict[str, str]]
    ) -> Optional[ActionCompletion]:
        """Attempts to return a function call from the LLM."""

    # TODO: make this return number 100% of time when OpenAI supports
    # JSONformer or logit masking or something similar.
    # Or massage this into action_completion for OpenAI and keep it for
    # Local AI.
    @abstractmethod
    async def digit_completions(
        self,
        query_messages: List[List[Message]],
    ) -> List[int]:
        """Returns an digit from the LLM (0-9)."""

    @abstractmethod
    async def embed(self, query: str) -> List[float]:
        """Embeds a piece of text."""

    @property
    @abstractmethod
    def embedding_size(self) -> int:
        """Embedding size."""
