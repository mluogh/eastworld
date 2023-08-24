import os
from glob import glob
from typing import List

from schema import GameDef


def load_game_from_json_string(json_string: str) -> GameDef:
    return GameDef.parse_raw(json_string)


def load_game_from_path(path: str) -> GameDef:
    with open(path, "r") as f:
        json_string = f.read()
    return load_game_from_json_string(json_string)


def load_games_from_path(path: str) -> List[GameDef]:
    suffix = "*.json"
    globs = glob(os.path.join(path, suffix))
    globs.sort()
    result_list: List[GameDef] = []
    for json_path in globs:
        result_list.append(load_game_from_path(json_path))
    return result_list
