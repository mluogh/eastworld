import os

from schema import Action, AgentDef, GameDef
from server.util.json_loader import (
    load_game_from_json_string,
    load_game_from_path,
    load_games_from_path,
)

test_game_def_1 = GameDef(
    name="test_game",
    description="for testing",
    agents=[
        AgentDef(
            name="test_agent",
            description="test agent",
            core_facts="for testing",
            instructions="confirm code works",
            example_speech="...",
            actions=[Action(name="mock_action", description="do nothing")],
        )
    ],
)

test_game_def_2 = GameDef(
    name="test_game_2",
    description="for testing again",
    agents=[
        AgentDef(
            name="test_agent_2",
            description="test agent 2",
            core_facts="for testing once more",
            instructions="confirm code works well",
            example_speech="... failed",
            actions=[Action(name="mock_action_2", description="do something")],
        )
    ],
)

test_games = [test_game_def_1, test_game_def_2]


def test_load_agent_from_json_string():
    string_def = GameDef.json(test_game_def_1)
    assert load_game_from_json_string(string_def) == test_game_def_1


def test_load_agent_from_file():
    script_dir = os.path.dirname(__file__)
    path = "example_data/game.json"
    abs_file_path = os.path.join(script_dir, path)
    result = load_game_from_path(abs_file_path)
    assert result.copy(exclude={"uuid", "agents"}) == test_game_def_1.copy(
        exclude={"uuid", "agents"}
    )
    assert result.agents[0].copy(exclude={"uuid"}) == test_game_def_1.agents[0].copy(
        exclude={"uuid"}
    )


def test_load_agents_from_file():
    script_dir = os.path.dirname(__file__)
    path = "example_data"
    abs_file_path = os.path.join(script_dir, path)
    result = load_games_from_path(abs_file_path)
    for i in range(len(result)):
        game = result[i]
        expected_game = test_games[i]
        assert game.copy(exclude={"uuid", "agents"}) == expected_game.copy(
            exclude={"uuid", "agents"}
        )
        assert game.agents[0].copy(exclude={"uuid"}) == expected_game.agents[0].copy(
            exclude={"uuid"}
        )
