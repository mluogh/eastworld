from typing import List, Optional, Union

from pydantic import BaseModel, Field

from schema import ActionCompletion, Message


class MessageWithDebug(BaseModel):
    message: Message
    debug: List[Message] = Field(default_factory=list)


class ActionCompletionWithDebug(BaseModel):
    action: Optional[ActionCompletion]
    debug: List[Message] = Field(default_factory=list)


class InteractWithDebug(BaseModel):
    response: Union[Message, ActionCompletion]
    debug: List[Message] = Field(default_factory=list)
