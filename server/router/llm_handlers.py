from typing import List

from fastapi import APIRouter, Depends

from llm.base import LLMBase
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
