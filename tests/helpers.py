from copy import deepcopy
from typing import Any
from unittest.mock import AsyncMock


class AsyncCopyingMock(AsyncMock):
    def __call__(self, *args: Any, **kwargs: Any):
        args = deepcopy(args)
        kwargs = deepcopy(kwargs)
        return super(AsyncCopyingMock, self).__call__(*args, **kwargs)
