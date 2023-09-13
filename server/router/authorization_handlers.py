from fastapi import APIRouter, Depends, Query
from fastapi.responses import RedirectResponse
from requests_oauthlib import OAuth2Session

from schema.token_response import TokenResponse
from server.context import get_auth_provider_session
from server.security.auth import verify_google_id_token
from configparser import ConfigParser
from server.context import get_config_parser

router = APIRouter(
    prefix="/auth",
    tags=["Authorization"],
)


@router.get("/authorize")
async def authorize(
    parser: ConfigParser = Depends(get_config_parser),
    auth_provider_session: OAuth2Session = Depends(get_auth_provider_session),
) -> RedirectResponse:
    # Construct the URL to redirect the user to Google's OAuth2 authorization endpoint
    oauth2_authorization_url = parser.get(
        "oauth2",
        "AUTHORIZATION_URL",
        fallback="https://accounts.google.com/o/oauth2/auth",
    )
    auth_url, _ = auth_provider_session.authorization_url(  # type: ignore
        oauth2_authorization_url,
    )
    return RedirectResponse(auth_url)


@router.get("/callback", response_model=TokenResponse)
async def callback(
    code: str = Query(None, description="Authorization code"),
    # TODO: Add state
    state: str = Query(None, description="State parameter"),
    parser: ConfigParser = Depends(get_config_parser),
    auth_provider_session: OAuth2Session = Depends(get_auth_provider_session),
) -> TokenResponse:
    oauth2_token_url = parser.get(
        "oauth2",
        "TOKEN_URL",
        fallback="https://oauth2.googleapis.com/token",
    )
    oauth2_client_secret = parser.get(
        "oauth2",
        "CLIENT_SECRET",
        fallback="fake_secret",
    )
    tokens = auth_provider_session.fetch_token(  # type: ignore
        oauth2_token_url, code=code, client_secret=oauth2_client_secret
    )

    id_token = tokens["id_token"]

    verify_google_id_token(id_token, parser)

    return TokenResponse(id_token=id_token, expires_in_seconds=tokens["expires_in"])
