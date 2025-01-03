from sqlmodel import SQLModel,Field,Relationship
from typing import Optional
from datetime import date, datetime
from models.base_model import BaseModel


class GoalModel(BaseModel, table=True):
    goal_name:str
    target_amount:float
    current_savings:float
    start_date:date
    end_date:date
    progress_percentage:float|None = None
    priority:str
    status:str|None = Field(default="In Progress")
    user:Optional[int] = Field(default=None,foreign_key='usermodel.id')
    