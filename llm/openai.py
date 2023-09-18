import asyncio
import json
import os
import re
from typing import Any, Dict, List, Optional, Union

import openai
from aiohttp import ClientSession

from llm.base import LLMBase
from schema import ActionCompletion, Message


class OpenAIInterface(LLMBase):
    def __init__(
        self,
        api_key: str = "",
        model: str = "gpt-3.5-turbo",
        embedding_size: int = 1536,
        api_base: Optional[str] = None,
        client_session: Optional[ClientSession] = None,
    ):
        self._model = model
        self._embedding_size = embedding_size
        if api_key:
            openai.api_key = api_key
        else:
            openai.api_key = os.getenv("OPENAI_API_KEY")
        if api_base:
            openai.api_base = api_base
        # TODO: does this actually make it faster?
        openai.aiosession.set(client_session)

    async def completion(
        self,
        messages: List[Message],
        functions: List[Dict[str, str]],
    ) -> Union[Message, ActionCompletion]:
        chat_function_arguments = _generate_completions_function_args(functions)
        completion: Any = (
            await openai.ChatCompletion.acreate(  # type: ignore
                messages=_parse_messages(messages),
                model=self._model,
                **chat_function_arguments,
            )
        )["choices"][0]["message"]

        if completion.get("function_call"):
            func_call = completion.get("function_call")
            # TODO: Sometimes the arguments are malformed.
            try:
                args = json.loads(func_call["arguments"])
            except json.JSONDecodeError:
                args: Any = {}

            return ActionCompletion(action=func_call["name"], args=args)

        return Message(role="assistant", content=completion["content"])

    async def chat_completion(
        self,
        messages: List[Message],
    ) -> Message:
        completion: Any = (
            await openai.ChatCompletion.acreate(  # type: ignore
                messages=_parse_messages(messages),
                model=self._model,
            )
        )["choices"][0]["message"]["content"]

        return Message(role="assistant", content=completion)

    async def action_completion(
        self,
        messages: List[Message],
        functions: List[Dict[str, str]],
    ) -> Optional[ActionCompletion]:
        retries = 3

        chat_function_arguments = _generate_completions_function_args(functions)

        for _ in range(retries):
            completion: Any = (
                await openai.ChatCompletion.acreate(  # type: ignore
                    messages=_parse_messages(messages),
                    model=self._model,
                    **chat_function_arguments,
                )
            )["choices"][0]["message"]

            if completion.get("function_call"):
                func_call = completion.get("function_call")
                args = json.loads(func_call["arguments"])
                return ActionCompletion(action=func_call["name"], args=args)

            messages.append(Message(role="assistant", content=completion["content"]))

            messages.append(
                Message(
                    role="system",
                    content="That was not a function call. Please call a function.",
                )
            )

        return None

    async def digit_completions(
        self,
        query_messages: List[List[Message]],
    ) -> List[int]:
        completions = [
            self._digit_completion_with_retries(query_message)
            for query_message in query_messages
        ]

        return await asyncio.gather(*completions)

    async def digit_completion(self, query: str) -> int:
        return await self._digit_completion_with_retries(
            messages=[Message(role="user", content=query)]
        )

    async def embed(self, query: str) -> List[float]:
        return (
            await openai.Embedding.acreate(  # type: ignore
                input=query, model="text-embedding-ada-002"
            )
        )["data"][0]["embedding"]

    @property
    def embedding_size(self) -> int:
        return self._embedding_size

    async def _digit_completion_with_retries(self, messages: List[Message]) -> int:
        for _ in range(3):
            text = str(
                (
                    await openai.ChatCompletion.acreate(  # type: ignore
                        messages=_parse_messages(messages),
                        model=self._model,
                        temperature=0,
                        max_tokens=1,
                    )
                )["choices"][0]["message"]["content"]
            )

            # TODO: error handle
            match = re.search(r"\d", text)
            if match:
                return int(match.group())

            messages.append(Message(role="assistant", content=text))

            messages.append(
                Message(
                    role="system",
                    content="That was not a digit. Try again.",
                )
            )

        return -1


def _parse_messages(
    messages: List[Message],
) -> List[Dict[str, str]]:
    return [msg.dict() for msg in messages]


# We need to do this because empty array [] is not valid for functions arg
# in OpenAI client. So if it's empty we need to not include it.
def _generate_completions_function_args(
    functions: List[Dict[str, str]]
) -> Dict[str, List[Dict[str, str]]]:
    if len(functions) > 0:
        chat_function_arguments = dict(
            functions=functions,
        )
        return chat_function_arguments
    return {}
