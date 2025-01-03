from typing import Optional
from sqlmodel import Field, Relationship

from models.base_model import BaseModel


class AccountModel(BaseModel, table=True):
    bank_name:str
    account_type:str
    account_number:int = Field(max_length=15)
    current_balance:float
    status:bool = Field(default=True)
    user:Optional[int] = Field(default=None,foreign_key='usermodel.id')

    class Config:
        validate_assignemnt = True

    