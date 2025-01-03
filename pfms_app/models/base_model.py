from sqlmodel import SQLModel, Field
from datetime import datetime


class BaseModel(SQLModel):
    id:int|None = Field(default=None, primary_key=True)
    created_at:datetime = datetime.utcnow()
    created_by:int | None = None
    updated_at:datetime | None = None
    updated_by: int | None = None