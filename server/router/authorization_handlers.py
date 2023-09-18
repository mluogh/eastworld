from configparser import ConfigParser
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import RedirectResponse
from fastapi_sso.sso.github import GithubSSO  # type: ignore
from fastapi_sso.sso.google import GoogleSSO  # type: ignore
from jose import jwt

from server.context import get_config_parser, get_github_sso, get_google_sso
from server.security.auth import authenticate

router = APIRouter(
    prefix="/auth",
    tags=["Authorization"],
)


@router.get("/google_authorize", operation_id="google_authorize")
async def google_authorize(
    request: Request,
    client_redirect_uri: Optional[str] = Query(None),
    google_sso: GoogleSSO = Depends(get_google_sso),
) -> RedirectResponse:
    # Construct the URL to redirect the user to Google's OAuth2 authorization endpoint
    """Generate login url and redirect"""
    with google_sso:
        return await google_sso.get_login_redirect(
            redirect_uri=str(request.url_for("google_callback")),
            state=client_redirect_uri,
        )


@router.get("/google_callback", operation_id="google_callback")
async def google_callback(
    request: Request,
    google_sso: GoogleSSO = Depends(get_google_sso),
    parser: ConfigParser = Depends(get_config_parser),
):
    with google_sso:
        user = await google_sso.verify_and_process(
            request, redirect_uri=str(request.url_for("google_callback"))
        )
    if not user:
        raise HTTPException(status_code=401, detail="Google authentication failed")

    if not google_sso.state:
        raise HTTPException(status_code=404, detail="Client callback url not found")

    secret_key = parser.get("oauth2", "SECRET_KEY", fallback="secret_key")
    token = jwt.encode(user.dict(), key=secret_key, algorithm="HS256")

    response = RedirectResponse(url=google_sso.state)
    response.set_cookie(key="token", value=token, max_age=43200)
    return response


@router.get("/github_authorize", operation_id="github_authorize")
async def github_authorize(
    request: Request,
    client_redirect_uri: Optional[str] = Query(None),
    github_sso: GithubSSO = Depends(get_github_sso),
) -> RedirectResponse:
    # Construct the URL to redirect the user to Google's OAuth2 authorization endpoint
    """Generate login url and redirect"""
    with github_sso:
        return await github_sso.get_login_redirect(
            redirect_uri=str(request.url_for("github_callback")),
            state=client_redirect_uri,
        )


@router.get("/github_callback", operation_id="github_callback")
async def github_callback(
    request: Request,
    github_sso: GithubSSO = Depends(get_github_sso),
    parser: ConfigParser = Depends(get_config_parser),
):
    with github_sso:
        user = await github_sso.verify_and_process(
            request, redirect_uri=str(request.url_for("github_callback"))
        )
    if not user:
        raise HTTPException(status_code=401, detail="Github authentication failed")

    if not github_sso.state:
        raise HTTPException(status_code=404, detail="Client callback url not found")

    secret_key = parser.get("oauth2", "SECRET_KEY", fallback="secret_key")
    token = jwt.encode(user.dict(), key=secret_key, algorithm="HS256")
    response = RedirectResponse(url=github_sso.state, headers={"token": token})
    response.set_cookie(key="token", value=token, max_age=43200)
    return response


@router.get("/check", operation_id="check")
async def check(authorized: str = Depends(authenticate)):
    return {
        "isAuthenticated": True,
    }
