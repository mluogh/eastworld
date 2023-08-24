from typing import TYPE_CHECKING, List, Union

from redis.asyncio import Redis
from redis.asyncio.client import Pipeline

# see https://github.com/python/typeshed/issues/8242
if TYPE_CHECKING:
    RedisType = Redis[bytes]  # this is only processed by mypy

    async def pipeline_exec(pipe: Pipeline[bytes]) -> List[Union[bytes, None]]:
        return await pipe.execute()  # type: ignore

else:
    RedisType = Redis

    async def pipeline_exec(pipe: Pipeline) -> List[Union[bytes, None]]:
        return await pipe.execute()  # type: ignore
