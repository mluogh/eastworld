from typing import List, Union

from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import UUID4

from schema import GameDef, Lore
from server.context import get_redis
from server.schema.summary import GameDefSummary
from server.security.auth import authenticate, password_protected
from server.typecheck_fighter import RedisType, pipeline_exec

router = APIRouter(
    prefix="/game",
    tags=["Game Definitions"],
)

GAME_DEFS_SET = "GAME_DEFS"


@router.post(
    "/create",
    operation_id="create_game",
    response_model=GameDef,
    dependencies=[Depends(authenticate), Depends(password_protected)],
)
async def create_game_def(
    game_name: str,
    redis: RedisType = Depends(get_redis),
):
    game = GameDef(name=game_name)
    uuid = str(game.uuid)
    pipe = redis.pipeline()
    pipe.set(uuid, game.json())
    pipe.sadd(GAME_DEFS_SET, uuid)
    await pipeline_exec(pipe)
    return game


@router.get("/list", operation_id="list_games", response_model=List[GameDefSummary])
async def get_games_list(
    redis: RedisType = Depends(get_redis), authorized: str = Depends(authenticate)
):
    games = await redis.smembers(GAME_DEFS_SET)
    pipeline = redis.pipeline()

    for game in games:
        pipeline.get(game)

    results: List[Union[bytes, None]] = await pipeline_exec(pipeline)
    game_defs: List[GameDef] = [
        GameDef.parse_raw(result) for result in results if result
    ]
    return [GameDefSummary(**game_def.dict()) for game_def in game_defs]


@router.get("/{uuid}", operation_id="get_game", response_model=GameDef)
async def get_game_def(
    uuid: str,
    redis: RedisType = Depends(get_redis),
):
    jsoned = await redis.get(uuid)
    if not jsoned:
        raise HTTPException(status_code=404, detail="Game not found")

    return GameDef.parse_raw(jsoned)


@router.get(
    "/{uuid}/lore",
    operation_id="get_lore",
    response_model=List[Lore],
    dependencies=[Depends(authenticate)],
)
async def get_game_lore(
    uuid: str,
    redis: RedisType = Depends(get_redis),
):
    jsoned = await redis.get(uuid)
    if not jsoned:
        raise HTTPException(status_code=404, detail="Game not found")

    return GameDef.parse_raw(jsoned).shared_lore


@router.get("/{uuid}/json", operation_id="get_game_json")
async def get_game_def_json(
    uuid: str,
    redis: RedisType = Depends(get_redis),
):
    jsoned = await redis.get(uuid)
    if not jsoned:
        raise HTTPException(status_code=404, detail="Game not found")
    return jsonable_encoder(GameDef.parse_raw(jsoned))


@router.put(
    "/json",
    operation_id="create_game_json",
    dependencies=[Depends(authenticate), Depends(password_protected)],
)
async def update_game_def_json(
    jsoned_game: str,
    redis: RedisType = Depends(get_redis),
):
    game: GameDef = GameDef.parse_raw(jsoned_game)
    await update_game_def(str(game.uuid), game, overwrite_agents=True, redis=redis)


@router.put(
    "/{uuid}/update",
    operation_id="update_game",
    response_model=GameDef,
    dependencies=[Depends(authenticate), Depends(password_protected)],
)
async def update_game_def(
    uuid: str,
    game: GameDef,
    overwrite_agents: bool = False,
    redis: RedisType = Depends(get_redis),
):
    game.uuid = UUID4(uuid)
    pipe = redis.pipeline()
    if overwrite_agents:
        pipe.set(uuid, game.json())
        pipe.sadd(GAME_DEFS_SET, uuid)
        await pipeline_exec(pipe)
        return game

    jsoned = await redis.get(uuid)
    if not jsoned:
        pipe.set(uuid, game.json())
        pipe.sadd(GAME_DEFS_SET, uuid)
        await pipeline_exec(pipe)
        return game

    old_game = GameDef.parse_raw(jsoned)
    if old_game.agents:
        game.agents = old_game.agents
    pipe.set(uuid, game.json())
    pipe.sadd(GAME_DEFS_SET, uuid)
    await pipeline_exec(pipe)
    return game


@router.delete(
    "/{uuid}",
    operation_id="delete_game",
    dependencies=[Depends(authenticate), Depends(password_protected)],
)
async def delete_game_def(
    uuid: str,
    redis: RedisType = Depends(get_redis),
):
    pipe = redis.pipeline()
    pipe.delete(uuid)
    pipe.srem(GAME_DEFS_SET, uuid)
    await pipeline_exec(pipe)
