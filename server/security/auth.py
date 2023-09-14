from typing import Optional
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.requests import Request
from configparser import ConfigParser
from server.context import get_config_parser
from jose import jwt
from jose.exceptions import JWTError, ExpiredSignatureError


def verify_google_id_token(
    token: str,
    parser: ConfigParser,
):
    try:
        secret_key = parser.get("oauth2", "SECRET_KEY", fallback="secret_key")
        # Validate the token and return user info
        jwt.decode(token, secret_key, algorithms=["HS256"])

    except ExpiredSignatureError:
        # The token has expired
        raise HTTPException(status_code=401, detail="Expired token")

    except JWTError:
        # Invalid token
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
            verify_google_id_token(token, parser)
            return credentials
        return None


# TODO: This seems wrong, but we need to use the actual
#  instantiated scheme as the dependency function
bearer_scheme = OAuth2Bearer(bearerFormat="bearerToken")
