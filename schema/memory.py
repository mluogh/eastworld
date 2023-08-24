from __future__ import annotations

from typing import List, Optional, Set

from pydantic import UUID4, BaseModel, Field


class GameStage(BaseModel):
    """Represents the flow of time in a game."""

    stage: int = 0
    """ 
    Should be incremented when the player undergoes some sort of tranformation. Most 
    non-permanent memories from previous stages are removed (in order of importance) and
    memories from the same stage are heavily preferred during retrieval.
    """

    major: int = 0
    """ 
    Should be incremented when the player completes a major quest line. 
    completing a quest. This adds an exponentially decaying weight to the importance of 
    the memory.
    """

    minor: int = 0
    """ 
    This is used to indicate the passage of time to the LLM.
    """


class MemoryConfig(BaseModel):
    max_memories: int = 1024
    embedding_dims: int = Field(...)
    """The dimensions of the vector that the embedding models return.
    i.e. OpenAI ada-002 is 1536."""

    memories_returned: int = 5
    """How many memories to return."""


class Memory(BaseModel):
    importance: int = 0
    """ 
    A number from 1-10 indicating the importance of the memory. An importance of 0 
    means importance will be determined by the LLM.
    """

    description: str
    embedding: Optional[List[float]] = None
    timestamp: Optional[GameStage] = None


class Lore(BaseModel):
    known_by: Set[UUID4] = Field(default_factory=set)
    memory: Memory
