import uuid

from pydantic import UUID4, BaseModel


class GameDefSummary(BaseModel):
    uuid: UUID4 = uuid.uuid4()
    name: str

    description: str = ""
