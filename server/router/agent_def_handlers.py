from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import UUID4

from schema import AgentDef
from server.context import get_redis
from server.router.game_def_handlers import get_game_def, update_game_def
from server.typecheck_fighter import RedisType

router = APIRouter(prefix="/game/{game_uuid}/agent", tags=["Agent Definitions"])


@router.post("/create", operation_id="create_agent", response_model=AgentDef)
async def create_agent_def(
    game_uuid: str, agent_name: str, redis: RedisType = Depends(get_redis)
):
    game = await get_game_def(game_uuid, redis)

    agent = AgentDef(name=agent_name)
    game.agents.append(agent)

    await update_game_def(game_uuid, game=game, overwrite_agents=True, redis=redis)

    return agent


@router.get("/list", operation_id="list_agents", response_model=List[AgentDef])
async def get_games_list(game_uuid: str, redis: RedisType = Depends(get_redis)):
    game = await get_game_def(game_uuid, redis)
    return game.agents


@router.get("/{agent_uuid}", operation_id="get_agent", response_model=AgentDef)
async def get_agent_def(
    game_uuid: str,
    agent_uuid: str,
    redis: RedisType = Depends(get_redis),
):
    game = await get_game_def(game_uuid, redis)

    agent = next(
        (agent for agent in game.agents if str(agent.uuid) == agent_uuid), None
    )
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    return agent


@router.put("/{agent_uuid}", operation_id="update_agent", response_model=AgentDef)
async def update_agent_def(
    game_uuid: str,
    agent_uuid: str,
    agent: AgentDef,
    redis: RedisType = Depends(get_redis),
):
    game = await get_game_def(game_uuid, redis)

    index = next(
        (i for i, agent in enumerate(game.agents) if str(agent.uuid) == agent_uuid), -1
    )
    if index == -1:
        raise HTTPException(status_code=404, detail="Agent not found")

    agent.uuid = UUID4(agent_uuid)

    game.agents[index] = agent

    await update_game_def(game_uuid, game=game, overwrite_agents=True, redis=redis)

    return agent


@router.delete("/{agent_uuid}", operation_id="delete_agent")
async def delete_agent_def(
    game_uuid: str,
    agent_uuid: str,
    redis: RedisType = Depends(get_redis),
):
    game = await get_game_def(game_uuid, redis)

    game.agents = [agent for agent in game.agents if str(agent.uuid) != agent_uuid]

    await update_game_def(game_uuid, game=game, overwrite_agents=True, redis=redis)
