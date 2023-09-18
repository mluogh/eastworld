from typing import Any
from unittest import IsolatedAsyncioTestCase
import configparser

from fakeredis import aioredis
from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient

from schema import AgentDef, GameDef
from server.context import get_redis, get_config_parser
from server.main import app


class AgentHandlerTest(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self._redis_fake: Any = aioredis.FakeRedis()
        parser = configparser.ConfigParser()
        parser.read("example_config.ini")

        def get_test_redis():
            return self._redis_fake

        def get_test_parser():
            return parser

        app.dependency_overrides[get_redis] = get_test_redis
        app.dependency_overrides[get_config_parser] = get_test_parser
        self._client = AsyncClient(app=app, base_url="http://test")

        resp = await self._client.post(
            "/game/create", params={"game_name": "King Game"}
        )
        self._base_game_def = GameDef.parse_obj(resp.json())

    async def asyncTearDown(self):
        await self._redis_fake.flushall()

    async def test_create_agent(self):
        AGENT_NAME = "King"
        await self._client.post(
            "/game/{}/agent/create".format(self._base_game_def.uuid),
            params={"agent_name": AGENT_NAME},
        )

        response = await self._client.get(
            "/game/{}/agent/list".format(self._base_game_def.uuid)
        )

        assert response.json()[0]["name"] == AGENT_NAME

    async def test_update_agent(self):
        AGENT_NAME = "King"
        resp = await self._client.post(
            "/game/{}/agent/create".format(self._base_game_def.uuid),
            params={"agent_name": AGENT_NAME},
        )

        agent_def = AgentDef.parse_obj(resp.json())
        agent_def.description = "My description"

        resp = await self._client.put(
            "/game/{}/agent/{}".format(self._base_game_def.uuid, agent_def.uuid),
            json=jsonable_encoder(agent_def),
        )

        assert resp.status_code == 200

        resp = await self._client.get(
            "/game/{}/agent/{}".format(self._base_game_def.uuid, agent_def.uuid)
        )

        assert resp.json()["description"] == "My description"

    async def test_delete_agent(self):
        await self._client.post(
            "/game/{}/agent/create".format(self._base_game_def.uuid),
            params={"agent_name": "KING"},
        )

        resp = await self._client.post(
            "/game/{}/agent/create".format(self._base_game_def.uuid),
            params={"agent_name": "GRON"},
        )

        assert resp.status_code == 200
        uuid = resp.json()["uuid"]

        resp = await self._client.delete(
            "/game/{}/agent/{}".format(self._base_game_def.uuid, uuid),
        )

        assert resp.status_code == 200

        resp = await self._client.get(
            "/game/{}/agent/list".format(self._base_game_def.uuid)
        )

        assert len(resp.json()) == 1
        assert resp.json()[0]["name"] == "KING"
