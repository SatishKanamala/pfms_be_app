from fastapi import APIRouter,Depends,Response,Header,Request, BackgroundTasks
from fastapi.exceptions import HTTPException
from sqlmodel import Session, select, or_
from typing import Annotated,Any
from authlib.integrations.starlette_client import OAuth
import os
from dotenv import load_dotenv


from models.users_model import UserModel, BaseUserModel, UserLogin
from core.hash_password import hash_password, verify_password, create_access_token, decode_access_token
from core.db import session
from core.std_response import RestResponse
from core.auth import user
from utils.generate_password import send_email, generate_password


load_dotenv()

router = APIRouter()


@router.post('/register')
def user_create(user:UserModel, response:Response, session=session):
    user_mail = session.exec(select(UserModel).where(UserModel.email == user.email)).first()
    if user_mail:
        response.status_code = 400
        return RestResponse(error=f"{user_mail.email} is already exists")
    
    user_username = session.exec(select(UserModel).where(UserModel.username == user.username)).first()
    if user_username:
        response.status_code = 400
        return RestResponse(error=f"{user_username.username} is already exists")

    user.password = hash_password(user.password)
    session.add(user)
    session.commit()
    session.refresh(user)
    response.status_code = 201
    return RestResponse(data=user, message="Registered successfully")


@router.put('/update/{user_id}')
def user_update(user_id:int, user:BaseUserModel, response:Response, session=session, current_user=user):
    #Need to implement to current user is updating or not
    
    get_user = session.get(UserModel, user_id)
    if not get_user:
        response.status_code = 400
        return RestResponse(error=f"User not found")

    user_mail = session.exec(select(UserModel).where(UserModel.id != user_id,UserModel.email == user.email,)).first()
    if user_mail:
        response.status_code = 400
        return RestResponse(error=f"{user_mail.email} is already exists")
    
    user_username = session.exec(select(UserModel).where(UserModel.id != user_id,UserModel.username == user.username)).first()
    if user_username:
        response.status_code = 400
        return RestResponse(error=f"{user_username.username} is already exists")
    
    # Update user fields
    user_data = user.model_dump(exclude_unset=True)
    session.add(get_user.sqlmodel_update(user_data))
    session.commit()
    return RestResponse(data=user, message="Updated sucessfully")

@router.post('/login')
def user_login(user: UserLogin, response:Response, session=session):
    db_user = session.exec(select(UserModel).where(or_(UserModel.email==user.email, UserModel.username==user.username))).first()
 
    if not db_user:
        response.status_code = 400
        return RestResponse(error="Invalid Email/Username")
    
    if not verify_password(user.password, db_user.password):
        response.status_code = 400
        return RestResponse(error="Invalid Password")
    
    token = create_access_token(data={"username":db_user.username,"user_id":db_user.id})
    return RestResponse(data={"token":token}, message="Login success")


@router.get("/user-info")
def user_info(response:Response, session=session, current_user=user):
    if current_user:
        from datetime import datetime
        current_hour = datetime.now().hour

        if 5 <= current_hour < 12:
            greeting = "Good Morning"
        elif 12 <= current_hour < 17:
            greeting = "Good Afternoon"
        else:
            greeting = "Good Evening"
        
        profile_pic = session.get(UserModel, current_user.get("user_id")).profile_pic

        data = {"username": current_user.get("username"), "greeting": greeting, "profile_pic":profile_pic}
        return RestResponse(data=data)
    else:
        return RestResponse(error="No data")


from pydantic import BaseModel
from google.oauth2 import id_token
from google.auth.transport import requests

class GoogleToken(BaseModel):
    token: str

@router.post("/login/google")
async def login_with_google(payload: GoogleToken, background_tasks: BackgroundTasks, session=session, ):
    try:
        # Old Code for Token Validation
        idinfo = id_token.verify_oauth2_token(
            payload.token,
            requests.Request(),
            "985346293558-iaff7dse11icdvs4v2e1n241tcmlglbq.apps.googleusercontent.com"
        )
  
        # Extract user details from idinfo
        user_email = idinfo["email"]
        user_name = idinfo.get("name", "")
        profile_pic = idinfo.get("picture", "")
        print(idinfo, "$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")

        db_user_email = session.exec(select(UserModel).where(UserModel.email==user_email)).first()

        password = generate_password()
        user = UserModel(email=user_email, password=hash_password(password), username=user_name, profile_pic=profile_pic)

        msg = "Login success"
        if not db_user_email:
            session.add(user)
            session.commit()
            subject = "Genereated password"
            recipient = user_email
            background_tasks.add_task(send_email, subject=subject, recipient=[recipient], password=password, username=user_name)
            msg = "Your accout is successfully created using Google, redirecting to home page. Check your mail for password."

        user_id = db_user_email.id if db_user_email else user.id
        token = create_access_token(data={"username":user_name,"user_id": user_id})
        return RestResponse(data={"token":token}, message=msg)
      
    except ValueError as e:
        raise HTTPException(status_code=401, detail="Invalid Google token")
