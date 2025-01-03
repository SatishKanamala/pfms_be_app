from sqlmodel import SQLModel,Field,Relationship
from typing import Optional
from models.base_model import BaseModel

class CategoryModel(BaseModel,table=True):
    name:str 
    description:str 
    is_income_generating:bool
    user:Optional[int] = Field(default=None,foreign_key='usermodel.id')