from sqlmodel import SQLModel, Field
from typing import Optional
from pydantic import EmailStr, validator
from datetime import date, datetime

from enums import Gender 

class BaseUserModel(SQLModel):
    first_name:Optional[str] = Field(default=None, min_length=1, max_length=50, description="Fisrt name of user")
    last_name:Optional[str] = Field(default=None, min_length=1, max_length=50, description="Last name of user")
    email:EmailStr = Field(unique=True, description="User's unique email address")
    username:str = Field(unique=True, description="Uses's unique username")
    phone_number:Optional[str] = Field(default=None, description="User's mobile number with country code")
    gender:Optional[Gender] = Field(default=None, description="Gender of the user")
    date_of_birth:Optional[date] = Field(default=None, description="Date of birth of the user")
    profile_pic:Optional[str] = Field(default=None, description="User's profile picture url")
    qualification:Optional[str] = Field(default=None, description="User's Qualification details")
    address:Optional[str] = Field(default=None, description="User's address details")
    # created_at:datetime = Field(default=datetime.utcnow())  # need to update in db

    def validate_date_of_birth(cls, value):
        if value is None:
            return
        val = datetime.strptime(value, "%Y-%m-%d").date()
        if value and val > date.today():
            raise ValueError("Date of birth cannot be future")
    

class UserModel(BaseUserModel, table=True):
    id:int | None = Field(default=None, primary_key=True)
    password:str = Field(..., min_length=8, description="Password with minimum length 8 characters")

    def __init__(self, **data):
        super().__init__(**data)
        self.validate_date_of_birth(self.date_of_birth)
        self.validate_password(self.password)

    def validate_password(cls, value):
        if not any(char.isupper() for char in value):
            raise ValueError("Password must contain atleast one uppercase letter")
        if not any(char.islower() for char in value):
            raise ValueError("Password must contain atleast one lowercase letter")
        if not any(char.isdigit() for char in value):
            raise ValueError("Password must contain atleast one digit")
        if not any(not char.isalnum() for char in value):
            raise ValueError("Password must contain atleast one special character")
    
    
class UserLogin(SQLModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: str



