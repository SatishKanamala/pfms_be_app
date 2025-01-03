from fastapi import APIRouter,Depends,Response,status
from sqlmodel import Session,select
from datetime import datetime

from models.accounts_model import AccountModel
from core.db import session
from core.auth import user
from core.std_response import RestResponse


router = APIRouter()


@router.post("/create")
def account_create(account:AccountModel, response:Response, session=session, user=user):
    account.user = user.get('user_id')
    account.created_by = user.get('user_id')
    session.add(account)
    session.commit()
    session.refresh(account)
    response.status_code = status.HTTP_201_CREATED
    return RestResponse(data=account, message="Account created successfully") 


@router.get("/get/{account_id}")
def account_get(account_id:int, response:Response, session=session, user=user):
    get_account = session.exec(select(AccountModel).where(AccountModel.user==user.get('user_id'), AccountModel.id==account_id)).first()
    if not get_account:
        response.status_code = 400
        return RestResponse(error=f"No account data")
    return RestResponse(data=get_account)


@router.get("/get_all")
def account_get_all(response:Response, session=session, user=user):
    get_account = session.exec(select(AccountModel).where(AccountModel.user==user.get('user_id'))).all()
    if not get_account:
        response.status_code = 400
        return RestResponse(error=f"No account data")
    return RestResponse(data=get_account)


@router.put("/update/{account_id}")
def account_update(account_id:int, account:AccountModel, response:Response, session=session, user=user):
    get_account = session.get(AccountModel,account_id)
    if not get_account:
        response.status_code = 400 
        return RestResponse(error=f'Account not found')
    account.updated_by = user.get('user_id')
    account.updated_at = datetime.utcnow()
    account_data = account.model_dump(exclude_unset=True)
    session.add(get_account.sqlmodel_update(account_data))
    session.commit()
    return RestResponse(data = account_data, message = f"{account.bank_name} Updated sucessfully")

@router.delete('/delete/{account_id}')
def account_delete(account_id:int, response:Response, session=session, user=user):
    get_account = session.get(AccountModel,account_id)
    if not get_account:
        response.status_code = 400
        return RestResponse(error=f'Account not found')
    session.delete(get_account)
    session.commit()
    response.status_code = 200
    return RestResponse(message=f'{get_account.bank_name} deleted successfully')

