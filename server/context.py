from configparser import ConfigParser

from fastapi import Request
from pydantic import UUID4

from game.session import Session
from llm.base import LLMBase

SessionsType = dict[UUID4, Session]


def get_redis(request: Request):
    return request.state.redis_client


def get_sessions(request: Request) -> SessionsType:
    return request.state.sessions


def get_config_parser(request: Request) -> ConfigParser:
    return request.state.parser


def get_llm(request: Request) -> LLMBase:
    return request.state.llm
