import uuid
from typing import List, Literal, Optional

from pydantic import UUID4, BaseModel, Field

from schema.agent import AgentDef
from schema.memory import Lore


class Message(BaseModel):
    role: Literal["user", "system", "assistant"]
    content: str


class Conversation(BaseModel):
    # TODO: perhaps have two or more `correspondents` if we have
    # agents speaking to each other?
    correspondent: Optional[AgentDef] = None
    """ The other party with whom the agent is speaking. """
    scene_description: Optional[str] = None
    instructions: Optional[str] = None
    """Provide context to the conversation and further directions for the LLM."""

    # TODO: with JSONformer, we *could* have these return non-digit completions
    queries: List[str] = Field(default_factory=list)
    """Ask the LLM a question about how the character is feeling. You can 
    use {agent} to autofill the name and {player} to autofill the player.
    e.g. How suspicious is {agent} that he is being suspected of murder?
    
    It will return a number from 1-5 or -1 if an error with LLM occurs.

    This string is automatically prepended for the query:
    "Based on the previous conversation, "
    """

    memories_to_include: Optional[int] = None
    """How many memories are included in the prompt. If it's an important
    conversation, you may want to set this higher than default."""


class GameDef(BaseModel):
    uuid: UUID4 = Field(default_factory=uuid.uuid4)
    name: str

    description: str = ""
    """A general description of the world of the game that every agent will be informed 
    of in every conversation. Should only answer the 5 Ws and tone."""

    agents: List[AgentDef] = Field(default_factory=list)

    shared_lore: List[Lore] = Field(default_factory=list)
    """Lore/events/memories that more than one characters remember."""

    # TODO: add communities
    # communities:
