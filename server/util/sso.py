from configparser import ConfigParser
from fastapi_sso.sso.google import GoogleSSO  # type: ignore


def generate_google_sso(parser: ConfigParser) -> GoogleSSO:
    client_id = parser.get("oauth2", "CLIENT_ID", fallback="dummy_client_id")
    redirect_uri = parser.get(
        "oauth2", "REDIRECT_URI", fallback="http://localhost:8000/auth/callback"
    )
    scope = parser.get("oauth2", "SCOPES", fallback="openid,profile,email").split(",")
    client_secret = parser.get(
        "oauth2",
        "CLIENT_SECRET",
        fallback="fake_secret",
    )

    return GoogleSSO(
        client_id=client_id,
        scope=scope,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
    )