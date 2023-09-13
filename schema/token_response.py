from pydantic import BaseModel

class TokenResponse(BaseModel):
    id_token: str
    expires_in_seconds: int
