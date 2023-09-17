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
        return jwt.decode(token, secret_key, algorithms=["HS256"])

    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Expired token")

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


class OAuth2Bearer(HTTPBearer):
    def __init__(self, bearerFormat: str):
        super().__init__(bearerFormat=bearerFormat)

    async def __call__(
        self, request: Request, parser: ConfigParser = Depends(get_config_parser)
    ):
        use_auth = parser.getboolean("server", "auth_required", fallback=False)
        if use_auth:
            token: Optional[str] = request.cookies.get("token")
            if not token:
                raise HTTPException(
                    status_code=401, detail="No token provided in cookies"
                )
            user = verify_token(token, parser)
            if "email" not in user:
                raise HTTPException(status_code=401, detail="No email provided.")

            request.state.email = user["email"]
            credentials = HTTPAuthorizationCredentials(
                scheme="Bearer", credentials=token
            )
            return credentials
        return None


authenticate = OAuth2Bearer(bearerFormat="bearerToken")


def password_protected(
    password: str = Header(None), parser: ConfigParser = Depends(get_config_parser)
):
    is_production = parser.get("server", "environment", fallback="dev") == "prod"
    protected_resource_password = parser.get(
        "oauth2", "PROTECTED_RESOURCE_PASSWORD", fallback=""
    )
    if is_production and password != protected_resource_password:
        raise HTTPException(status_code=401, detail="Invalid password for resource")

    return password
