from datetime import datetime

from pydantic import BaseModel


class Data(BaseModel):
    title: str
    timestamp: datetime
    description: str | None = None
