from configparser import ConfigParser
from typing import Optional

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
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
            credentials: Optional[
                HTTPAuthorizationCredentials
            ] = await super().__call__(request)
            if not credentials:
                raise HTTPException(
                    status_code=401, detail="No Authorization header provided"
                )
            token = credentials.credentials
            user = verify_token(token, parser)
            if "email" not in user:
                raise HTTPException(status_code=401, detail="No email provided.")

            request.state.email = user["email"]
            return credentials
        return None


authenticate = OAuth2Bearer(bearerFormat="bearerToken")
