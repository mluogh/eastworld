import configparser
from typing import Any
from unittest import IsolatedAsyncioTestCase

from fakeredis import aioredis
from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient
from pydantic import UUID4

from schema import GameDef
from server.context import get_config_parser, get_redis
from server.main import app


class GameHandlerTest(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self._redis_fake: Any = aioredis.FakeRedis()
        parser = configparser.ConfigParser()
        parser.read("example_config.ini")

        def get_test_parser():
            return parser

        def get_test_redis():
            return self._redis_fake

        app.dependency_overrides[get_config_parser] = get_test_parser
        app.dependency_overrides[get_redis] = get_test_redis
        self._client = AsyncClient(app=app, base_url="http://test")

    async def asyncTearDown(self):
        await self._redis_fake.flushall()

    async def test_create_game(self):
        game_name = "King Game"
        response = await self._client.post(
            "/game/create", params={"game_name": game_name}
        )

        uuid = UUID4(response.json()["uuid"])
        assert response.status_code == 200
        assert response.json()["name"] == game_name

        game: GameDef = GameDef.parse_obj(response.json())

        response = await self._client.get("/game/{}".format(uuid))

        assert game == GameDef.parse_obj(response.json())

    async def test_save_game(self):
        game_name = "King Game"
        response = await self._client.post(
            "/game/create", params={"game_name": game_name}
        )

        assert response.status_code == 200
        assert response.json()["name"] == game_name

        game_def = GameDef.parse_obj(response.json())
        king_description = "This describes my game"
        game_def.description = king_description

        response = await self._client.put(
            "/game/{}/update".format(game_def.uuid),
            json=jsonable_encoder(game_def),
        )
        assert response.status_code == 200

        response = await self._client.get("/game/{}".format(game_def.uuid))
        assert response.status_code == 200
        assert response.json()["description"] == king_description

    async def test_delete_game(self):
        game_name = "King Game"
        create_resp = await self._client.post(
            "/game/create", params={"game_name": game_name}
        )
        uuid = create_resp.json()["uuid"]

        list_resp = await self._client.get("/game/list")
        assert len(list_resp.json()) == 1
        assert list_resp.json()[0]["uuid"] == uuid
        assert list_resp.json()[0]["name"] == game_name

        await self._client.delete("/game/{}".format(uuid))

        list_resp = await self._client.get("/game/list")
        assert len(list_resp.json()) == 0


# TODO: test no accidental agent override?
