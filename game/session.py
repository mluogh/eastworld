from dataclasses import dataclass
from typing import List

from pydantic import UUID4

from game.agent import GenAgent
from schema.game import GameDef


@dataclass
class Session:
    uuid: UUID4
    game_def: GameDef
    agents: List[GenAgent]
