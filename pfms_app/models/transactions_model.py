from sqlmodel import SQLModel,Field,Relationship
from typing import Optional
from models.base_model import BaseModel

class TransactionModel(BaseModel, table=True):
    amount:float
    description:str
    transaction_type:str
    user:Optional[int] = Field(default=None,foreign_key='usermodel.id')
    category:Optional[int] = Field(default=None,foreign_key='categorymodel.id')
    account:Optional[int] = Field(default=None,foreign_key='accountmodel.id')

class IncomeModel(BaseModel, table=True):
    amount:float
    description:str
    user:Optional[int] = Field(default=None,foreign_key='usermodel.id')
    category:Optional[int] = Field(default=None,foreign_key='categorymodel.id')
    account:Optional[int] = Field(default=None,foreign_key='accountmodel.id')

class ExpenseModel(BaseModel, table=True):
    amount:float
    description:str
    user:Optional[int] = Field(default=None,foreign_key='usermodel.id')
    category:Optional[int] = Field(default=None,foreign_key='categorymodel.id')
    account:Optional[int] = Field(default=None,foreign_key='accountmodel.id')


