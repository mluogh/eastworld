from configparser import ConfigParser
from typing import Optional

from fastapi import Depends, Header, HTTPException
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTError
from starlette.requests import Request

from server.context import get_config_parser


def verify_token(
    token: str,
    parser: ConfigParser,
):
    try:
        secret_key = parser.get("oauth2", "SECRET_KEY", fallback="secret_key")
        # Validate the token and return user info
        jwt.decode(token, secret_key, algorithms=["HS256"])

    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Expired token")

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    return None


class OAuth2Bearer(HTTPBearer):
    def __init__(self, bearerFormat: str):
        super().__init__(bearerFormat=bearerFormat)

    # We inject config parser here as this is part of the call stack.
    # Somewhat unconventional, if there is a better way to do this, please
    # make a pr.
    async def __call__(
        self, request: Request, parser: ConfigParser = Depends(get_config_parser)
    ):
        use_auth = parser.getboolean("server", "auth_required", fallback=False)
        if use_auth:
            credentials: Optional[
                HTTPAuthorizationCredentials
            ] = await super().__call__(request)
            if not credentials:
                raise HTTPException(
                    status_code=401, detail="No Authorization header provided"
                )
            token = credentials.credentials
            verify_token(token, parser)
            return credentials
        return None


bearer_scheme = OAuth2Bearer(bearerFormat="bearerToken")


def protected_resource(
    password: str = Header(...), parser: ConfigParser = Depends(get_config_parser)
):
    production = parser.get("server", "environment", fallback="dev") == "prod"
    protected_resource_password = parser.get(
        "oauth2", "PROTECTED_RESOURCE_PASSWORD", fallback="pass"
    )
    if production and password != protected_resource_password:
        raise HTTPException(status_code=401, detail="Invalid password for resource")

    return password
