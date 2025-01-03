from sqlmodel import SQLModel,Field,Relationship
from typing import Optional
from datetime import date, datetime
from models.base_model import BaseModel


class BudgetModel(BaseModel, table=True):
    start_date:date|None = None
    end_date:date|None = None
    amount:float
    description:str
    user:Optional[int] = Field(default=None,foreign_key='usermodel.id')
    category:Optional[int] = Field(default=None,foreign_key='categorymodel.id')
