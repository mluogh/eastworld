from typing import Optional
from google.oauth2 import id_token
from google.auth.transport import requests
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from google.auth.exceptions import GoogleAuthError
from starlette.requests import Request
from configparser import ConfigParser
from server.context import get_config_parser


def verify_google_id_token(
    token: str,
    parser: ConfigParser,
):
    try:
        client_id = parser.get("oauth2", "CLIENT_ID", fallback="dummy_client_id")
        # Validate the token and return user info
        id_token.verify_oauth2_token(token, requests.Request(), client_id)  # type: ignore

    except ValueError:
        # Invalid token
        raise HTTPException(status_code=401, detail="Invalid token")
    except GoogleAuthError:
        # Invalid token
        raise HTTPException(status_code=401, detail="Invalid issuer")
    return None


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
            verify_google_id_token(token, parser)
            return credentials
        return None


# TODO: This seems wrong, but we need to use the actual
#  instantiated scheme as the dependency function
bearer_scheme = OAuth2Bearer(bearerFormat="bearerToken")
