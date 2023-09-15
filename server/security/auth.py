from typing import Optional
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.requests import Request
from configparser import ConfigParser
from server.context import get_config_parser
from jose import jwt
from jose.exceptions import JWTError, ExpiredSignatureError


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
            token: Optional[str] = request.cookies.get("token")
            if not token:
                raise HTTPException(
                    status_code=401, detail="No token provided in cookies"
                )
            verify_token(token, parser)
            credentials = HTTPAuthorizationCredentials(
                scheme="Bearer", credentials=token
            )
            return credentials
        return None


bearer_scheme = OAuth2Bearer(bearerFormat="bearerToken")
