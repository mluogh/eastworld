from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi_sso.sso.google import GoogleSSO  # type: ignore
from configparser import ConfigParser

from jose import jwt

from server.context import get_google_sso, get_config_parser


router = APIRouter(
    prefix="/auth",
    tags=["Authorization"],
)


@router.get("/google_authorize")
async def google_authorize(
    request: Request,
    google_sso: GoogleSSO = Depends(get_google_sso),
) -> RedirectResponse:
    # Construct the URL to redirect the user to Google's OAuth2 authorization endpoint
    """Generate login url and redirect"""
    with google_sso:
        return await google_sso.get_login_redirect(
            redirect_uri=str(request.url_for("google_callback"))
        )


@router.get("/google_callback")
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
    secret_key = parser.get("oauth2", "SECRET_KEY", fallback="secret_key")
    token = jwt.encode(user.dict(), key=secret_key, algorithm="HS256")
    response = JSONResponse(content={"token": token})
    response.set_cookie(key="token", value=token)
    return response
