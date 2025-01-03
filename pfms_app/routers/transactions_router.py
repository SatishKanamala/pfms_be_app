from fastapi import APIRouter,Depends,Response
from sqlmodel import Session,select
from datetime import datetime

from models.transactions_model import TransactionModel
from core.db import session
from core.auth import user
from core.std_response import RestResponse

router = APIRouter()



@router.post('/create')
def transaction_create(transaction:TransactionModel, response:Response, session=session, current_user=user):
    transaction.user = current_user.get('user_id')
    transaction.created_by = current_user.get('user_id')
    session.add(transaction)
    session.commit()
    session.refresh(transaction)
    response.status_code = 201
    return RestResponse(data = transaction, message = f"Transaction created Successfully")
    

@router.get('/get/{transaction_id}')
def transaction_get(response:Response, session=session, current_user=user, transaction_id:int|None = None):
    data = session.exec(select(TransactionModel).where(TransactionModel.user == current_user.get("user_id"),TransactionModel.id == transaction_id)).first()
    if not data:
        response.status_code = 400
        return RestResponse(error="No data found")
    return RestResponse(data=data)


@router.get('/get_all/')
def transaction_list(response:Response, session=session, current_user=user):
    data = session.exec(select(TransactionModel).where(TransactionModel.user == current_user.get("user_id"))).all()
    if not data:
        response.status_code = 400
        return RestResponse(error="No data found")
    return RestResponse(data=data)


@router.put('/update/{transaction_id}')
def transaction_update(transaction:TransactionModel, response:Response, session=session, current_user=user, transaction_id:int|None = None):
    get_transaction = session.get(TransactionModel, transaction_id)
    if not get_transaction:
        response.status_code = 400
        return RestResponse(error="transaction not found")
    
    transaction.updated_by = current_user.get('user_id')
    transaction.updated_at = datetime.utcnow()
    transaction_data = transaction.model_dump(exclude_unset=True)
    session.add(get_transaction.sqlmodel_update(transaction_data))
    session.commit()
    return RestResponse(data = transaction_data, message = f"Transaction Updated sucessfully")


@router.delete('/delete/{transaction_id}')
def transaction_delete(response:Response, session=session, current_user=user, transaction_id:int|None = None):
    get_transaction = session.get(TransactionModel, transaction_id)
    if not get_transaction:
        response.status_code = 400
        return RestResponse(error="transaction not found")
    
    session.delete(get_transaction)
    session.commit()
    response.status_code = 200
    return RestResponse(message = f"Transaction deleted successfully")


