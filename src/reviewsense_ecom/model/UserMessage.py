from pydantic import BaseModel


class UserMessage(BaseModel):
    message: str = "suggest me a mobile with okay battery backup"
