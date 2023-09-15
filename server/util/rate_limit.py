from configparser import ConfigParser

from fastapi import Request, Response
from fastapi_limiter.depends import RateLimiter  # type: ignore

parser = ConfigParser()
parser.read("config.ini")

enable_rate_limit = parser.getboolean("rate_limit", "enable_rate_limit", fallback=False)
times = parser.getint("rate_limit", "times", fallback=1)
seconds = parser.getint("rate_limit", "seconds", fallback=0)
minutes = parser.getint("rate_limit", "minutes", fallback=0)
hours = parser.getint("rate_limit", "hours", fallback=0)


async def user(request: Request):
    if parser.getboolean("server", "auth_required", fallback=False):
        return str(request.state.email)
    if request.client:
        ip, _ = request.client
        return ip
    raise Exception("No user found.")


base_limiter = RateLimiter(
    times=times, seconds=seconds, minutes=minutes, hours=hours, identifier=user
)


async def rate_limiter(
    request: Request,
    response: Response,
):
    if enable_rate_limit:
        await base_limiter(request, response)
