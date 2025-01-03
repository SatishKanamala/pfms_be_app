from sqlmodel import SQLModel,Field,Relationship
from typing import Optional
from datetime import date, datetime
from models.base_model import BaseModel


class InvestmentModel(BaseModel, table=True):
    name:str
    type:str
    category:str
    purchase_date:date
    initial_amount:float
    current_value:float|None = None
    return_value:float|None = None
    status:bool|None = Field(default=True)
    user:Optional[int] = Field(default=None,foreign_key='usermodel.id')
    