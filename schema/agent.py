from __future__ import annotations

import uuid
from typing import Any, Dict, List, Literal

from pydantic import UUID4, BaseModel, Field

from schema.memory import Lore, Memory


class Parameter(BaseModel):
    name: str = Field(..., regex="^[a-zA-Z0-9_-]{1,64}$")
    description: str
    type: Literal["number", "string", "boolean"] = "string"
    enum: List[str] = Field(default_factory=list)


class Action(BaseModel):
    name: str = Field(..., regex="^[a-zA-Z0-9_-]{1,64}$")
    description: str
    parameters: List[Parameter] = Field(default_factory=list)


class ActionCompletion(BaseModel):
    action: str
    args: Dict[str, Any]


class AgentDef(BaseModel):
    uuid: UUID4 = Field(default_factory=uuid.uuid4)

    is_playable: bool = False
    """
    Whether or not this represents a playable character.
    """

    name: str
    description: str = ""
    """A biography of the agent; its general disposition, life goals etc."""

    core_facts: str = ""
    """Core facts that the agent knows. E.g.: 
    He has a dog named Biscuit.
    He knows Biscuit is responsible for the greatest bank heist of the century"""

    instructions: str = ""
    """General instructions on behaviour and manner of speech."""

    example_speech: str = ""
    """To guide the LLM on how this agent should speak. 
    E.g. "Ayy, I'm walkin' 'ere. Fuggedaboutit!" """

    # TODO: add communities
    # communities: List[str]
    # """A list of the communities this agent is part of.
    # The agent will be privy to community knowledge and description."""

    personal_lore: List[Memory] = Field(default_factory=list)
    """Hardcoded memories that the agent starts with. """

    actions: List[Action] = Field(default_factory=list)


class Knowledge(BaseModel):
    game_description: str
    shared_lore: List[Lore]
    agent_def: AgentDef
