from typing import List

from fastapi import APIRouter, Depends

from game.prompt_helpers import get_rate_function, rating_to_int
from llm.base import LLMBase
from schema import Message
from server.context import (
    get_llm,
)

router = APIRouter(
    prefix="/llm",
    tags=["LLM"],
)


@router.get("/embed", operation_id="embed", response_model=List[float])
async def embed(
    text: str,
    llm: LLMBase = Depends(get_llm),
) -> List[float]:
    return await llm.embed(text)


@router.get("/rate", operation_id="rate", response_model=int)
async def rate(
    question: str,
    llm: LLMBase = Depends(get_llm),
) -> int:
    rating = await llm.action_completion(
        [
            Message(
                role="system",
                content=question + " Please use the provided Rate() function.",
            )
        ],
        [get_rate_function()],
    )

    return rating_to_int(rating)
