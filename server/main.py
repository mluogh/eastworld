import configparser
import logging
import os
import pickle
from contextlib import asynccontextmanager
from typing import List

from aiohttp import ClientSession
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter  # type: ignore
from redis.asyncio import Redis

from llm.openai import OpenAIInterface
from schema import GameDef
from server.context import SessionsType
from server.router import (
    agent_def_handlers,
    authorization_handlers,
    game_def_handlers,
    llm_handlers,
    session_handlers,
    util_handlers,
)
from server.typecheck_fighter import pipeline_exec
from server.util.json_loader import load_games_from_path
from server.util.sso import generate_github_sso, generate_google_sso

GAMES_DEFS_SET = "GAME_DEFS"

# TODO: Add this to a config file


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_client: Redis[bytes] = Redis(
        host="localhost",
        port=6379,
    )
    sessions: SessionsType = {}
    parser = configparser.ConfigParser()
    parser.read("config.ini")

    use_local_llm = parser.getboolean("llm", "use_local_llm", fallback=False)
    api_base = "http://localhost:8080/v1" if use_local_llm else None

    key = parser.get("llm", "openai_api_key", fallback="Dummy key")
    chat_model = parser.get("llm", "chat_model")
    embedding_size = parser.getint("llm", "embedding_size")

    google_sso = generate_google_sso(parser=parser)
    github_sso = generate_github_sso(parser=parser)

    openai_http_client = ClientSession()
    llm = OpenAIInterface(
        api_key=key,
        model=chat_model,
        api_base=api_base,
        embedding_size=embedding_size,
        client_session=openai_http_client,
    )

    await FastAPILimiter.init(redis_client)  # type: ignore

    dev_mode = parser.getboolean("server", "dev_mode", fallback=False)
    if dev_mode:
        # getLogger returns the same singleton everywhere, so usages in
        # controllers should log to this stdout stream handler as well
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        logger.addHandler(handler)

        resp = await redis_client.get("sessions")
        if resp:
            sessions = pickle.loads(resp)
        game_defs = load_existing_game_defs_from_json(
            parser.get("server", "game_defs_path", fallback="")
        )
        pipe = redis_client.pipeline()
        for game in game_defs:
            pipe.set(str(game.uuid), game.json(), nx=True)
            pipe.sadd(GAMES_DEFS_SET, str(game.uuid))
        await pipeline_exec(pipe)

    yield {
        "redis_client": redis_client,
        "sessions": sessions,
        "parser": parser,
        "llm": llm,
        "google_sso": google_sso,
        "github_sso": github_sso,
    }

    if dev_mode:
        await redis_client.set("sessions", pickle.dumps(sessions))

    await redis_client.close()
    await openai_http_client.close()


def get_redis(request: Request):
    return request.state.redis_client


def load_existing_game_defs_from_json(game_defs_path: str) -> List[GameDef]:
    current_directory = os.path.dirname(__file__)
    abs_file_path = os.path.join(current_directory, game_defs_path)
    game_defs = load_games_from_path(abs_file_path)
    return game_defs


app = FastAPI(
    title="eastworld",
    version="0.0.1",
    description="generative game agents",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(util_handlers.router)
app.include_router(llm_handlers.router)
app.include_router(game_def_handlers.router)
app.include_router(agent_def_handlers.router)
app.include_router(session_handlers.router)
app.include_router(authorization_handlers.router)
