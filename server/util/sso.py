from configparser import ConfigParser
from fastapi_sso.sso.google import GoogleSSO  # type: ignore
from fastapi_sso.sso.github import GithubSSO  # type: ignore


def generate_google_sso(parser: ConfigParser) -> GoogleSSO:
    client_id = parser.get("oauth2", "GOOGLE_CLIENT_ID", fallback="dummy_client_id")
    scope = parser.get(
        "oauth2", "GOOGLE_SCOPES", fallback="openid,profile,email"
    ).split(",")
    client_secret = parser.get(
        "oauth2",
        "GOOGLE_CLIENT_SECRET",
        fallback="fake_secret",
    )

    return GoogleSSO(
        client_id=client_id,
        scope=scope,
        client_secret=client_secret,
    )


def generate_github_sso(parser: ConfigParser) -> GithubSSO:
    client_id = parser.get("oauth2", "GITHUB_CLIENT_ID", fallback="dummy_client_id")
    scope = parser.get(
        "oauth2", "GITHUB_SCOPES", fallback="openid,profile,email"
    ).split(",")
    client_secret = parser.get(
        "oauth2",
        "GITHUB_CLIENT_SECRET",
        fallback="fake_secret",
    )

    return GithubSSO(
        client_id=client_id,
        scope=scope,
        client_secret=client_secret,
    )
