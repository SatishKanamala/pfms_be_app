from fastapi import APIRouter,Depends,Response,Query
from sqlmodel import Session,select
from datetime import datetime
from sqlalchemy import func

from models.transactions_model import TransactionModel, IncomeModel, ExpenseModel
from models.budget_model import BudgetModel
from models.accounts_model import AccountModel
from core.db import session
from core.auth import user
from core.std_response import RestResponse

router = APIRouter()


@router.post('/create')
def transaction_create(transaction:TransactionModel, response:Response, session=session, current_user=user):
    total_budget = session.exec(select(func.sum(BudgetModel.amount))
                          .where(BudgetModel.category == transaction.category,
                                 BudgetModel.user == current_user.get('user_id'),
                                 transaction.created_at>=BudgetModel.start_date,
                                 transaction.created_at<=BudgetModel.end_date)).first()
    total_transaction_amount = session.exec(select(func.sum(TransactionModel.amount))
                                     .where(TransactionModel.category==transaction.category,
                                            TransactionModel.user==current_user.get('user_id'))).first()
    if total_budget  and total_budget <= float(transaction.amount):
        response.status_code = 400  # Bad Request
        return RestResponse(error="Transaction amount exceeds the allocated budget for this category.")

    if total_budget and total_transaction_amount and total_budget <= total_transaction_amount + float(transaction.amount):
        response.status_code = 400  # Bad Request
        return RestResponse(error="Transaction amount exceeds the allocated budget for this category.")

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
def transaction_list(
    response: Response,
    session=session, current_user=user, 
    limit: int = Query(7, ge=1),
    offset: int = Query(0, ge=0)  
):
    
    query = (
        select(TransactionModel)
        .where(TransactionModel.user == current_user.get("user_id"))
        .offset(offset)
        .limit(limit)
    )
    data = session.exec(query).all()

    if not data:
        response.status_code = 404
        return RestResponse(error="No data found")

    total_query = select(func.count()).where(TransactionModel.user == current_user.get("user_id"))
    total = session.exec(total_query).first()

    return RestResponse(
        data=data,
        metadata={
            "total": total,
            "limit": limit,
            "offset": offset
        }
    )


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


#Income-Routing
@router.post('/income/create')
def transaction_create(transaction:IncomeModel, response:Response, session=session, current_user=user):

    account = session.exec(select(AccountModel).where(AccountModel.user == current_user.get('user_id'),
                                                    AccountModel.id == transaction.account)).first()
    if account:
        account.current_balance += float(transaction.amount)

    # total_budget = session.exec(select(func.sum(BudgetModel.amount))
    #                       .where(BudgetModel.category == transaction.category,
    #                              BudgetModel.user == current_user.get('user_id'),
    #                              transaction.created_at>=BudgetModel.start_date,
    #                              transaction.created_at<=BudgetModel.end_date)).first()
    # total_transaction_amount = session.exec(select(func.sum(IncomeModel.amount))
    #                                  .where(IncomeModel.category==transaction.category,
    #                                         IncomeModel.user==current_user.get('user_id'))).first()
    # if total_budget  and total_budget <= float(transaction.amount):
    #     response.status_code = 400  # Bad Request
    #     return RestResponse(error="Transaction amount exceeds the allocated budget for this category.")

    # if total_budget and total_transaction_amount and total_budget <= total_transaction_amount + float(transaction.amount):
    #     response.status_code = 400  # Bad Request
    #     return RestResponse(error="Transaction amount exceeds the allocated budget for this category.")

    transaction.user = current_user.get('user_id')
    transaction.created_by = current_user.get('user_id')
    session.add(transaction)
    session.commit()
    session.refresh(transaction)
    response.status_code = 201
    return RestResponse(data = transaction, message = f"Transaction created Successfully")
    

@router.get('/income/get/{transaction_id}')
def transaction_get(response:Response, session=session, current_user=user, transaction_id:int|None = None):
    data = session.exec(select(IncomeModel).where(IncomeModel.user == current_user.get("user_id"),IncomeModel.id == transaction_id)).first()
    if not data:
        response.status_code = 400
        return RestResponse(error="No data found")
    return RestResponse(data=data)

@router.get('/income/get_all/')
def transaction_list(
    response: Response,
    session=session, current_user=user, 
    limit: int = Query(7, ge=1),
    offset: int = Query(0, ge=0)  
):
    
    query = (
        select(IncomeModel)
        .where(IncomeModel.user == current_user.get("user_id"))
        .offset(offset)
        .limit(limit)
    )
    data = session.exec(query).all()

    if not data:
        response.status_code = 404
        return RestResponse(error="No data found")

    total_query = select(func.count()).where(IncomeModel.user == current_user.get("user_id"))
    total = session.exec(total_query).first()

    return RestResponse(
        data=data,
        metadata={
            "total": total,
            "limit": limit,
            "offset": offset
        }
    )


@router.put('/income/update/{transaction_id}')
def transaction_update(transaction:IncomeModel, response:Response, session=session, current_user=user, transaction_id:int|None = None):
    get_transaction = session.get(IncomeModel, transaction_id)
    if not get_transaction:
        response.status_code = 400
        return RestResponse(error="transaction not found")
    
    transaction.updated_by = current_user.get('user_id')
    transaction.updated_at = datetime.utcnow()
    transaction_data = transaction.model_dump(exclude_unset=True)
    session.add(get_transaction.sqlmodel_update(transaction_data))
    session.commit()
    return RestResponse(data = transaction_data, message = f"Transaction Updated sucessfully")


@router.delete('/income/delete/{transaction_id}')
def transaction_delete(response:Response, session=session, current_user=user, transaction_id:int|None = None):
    get_transaction = session.get(IncomeModel, transaction_id)
    if not get_transaction:
        response.status_code = 400
        return RestResponse(error="transaction not found")
    
    session.delete(get_transaction)
    session.commit()
    response.status_code = 200
    return RestResponse(message = f"Transaction deleted successfully")



#Expense-Routing
@router.post('/expense/create')
def transaction_create(transaction:ExpenseModel, response:Response, session=session, current_user=user):

    account = session.exec(select(AccountModel).where(AccountModel.user == current_user.get('user_id'),
                                                    AccountModel.id == transaction.account)).first()
    if account:
        if account.current_balance >= float(transaction.amount):
            account.current_balance -= float(transaction.amount)
        else:
            response.status_code = 400
            return RestResponse(error="Insufficient account balance")

    total_budget = session.exec(select(func.sum(BudgetModel.amount))
                          .where(BudgetModel.category == transaction.category,
                                 BudgetModel.user == current_user.get('user_id'),
                                 transaction.created_at>=BudgetModel.start_date,
                                 transaction.created_at<=BudgetModel.end_date)).first()
    total_transaction_amount = session.exec(select(func.sum(ExpenseModel.amount))
                                     .where(ExpenseModel.category==transaction.category,
                                            ExpenseModel.user==current_user.get('user_id'))).first()
    if total_budget  and total_budget <= float(transaction.amount):
        response.status_code = 400  # Bad Request
        return RestResponse(error="Transaction amount exceeds the allocated budget for this category.")

    if total_budget and total_transaction_amount and total_budget <= total_transaction_amount + float(transaction.amount):
        response.status_code = 400  # Bad Request
        return RestResponse(error="Transaction amount exceeds the allocated budget for this category.")
    
    
    transaction.user = current_user.get('user_id')
    transaction.created_by = current_user.get('user_id')
    session.add(transaction)
    session.commit()
    session.refresh(transaction)
    response.status_code = 201
    return RestResponse(data = transaction, message = f"Transaction created Successfully")
    

@router.get('/expense/get/{transaction_id}')
def transaction_get(response:Response, session=session, current_user=user, transaction_id:int|None = None):
    data = session.exec(select(ExpenseModel).where(ExpenseModel.user == current_user.get("user_id"),ExpenseModel.id == transaction_id)).first()
    if not data:
        response.status_code = 400
        return RestResponse(error="No data found")
    return RestResponse(data=data)

@router.get('/expense/get_all/')
def transaction_list(
    response: Response,
    session=session, current_user=user, 
    limit: int = Query(7, ge=1),
    offset: int = Query(0, ge=0)  
):
    
    query = (
        select(ExpenseModel)
        .where(ExpenseModel.user == current_user.get("user_id"))
        .offset(offset)
        .limit(limit)
    )
    data = session.exec(query).all()

    if not data:
        response.status_code = 404
        return RestResponse(error="No data found")

    total_query = select(func.count()).where(ExpenseModel.user == current_user.get("user_id"))
    total = session.exec(total_query).first()

    return RestResponse(
        data=data,
        metadata={
            "total": total,
            "limit": limit,
            "offset": offset
        }
    )


@router.put('/expense/update/{transaction_id}')
def transaction_update(transaction:ExpenseModel, response:Response, session=session, current_user=user, transaction_id:int|None = None):
    get_transaction = session.get(ExpenseModel, transaction_id)
    if not get_transaction:
        response.status_code = 400
        return RestResponse(error="transaction not found")
    
    transaction.updated_by = current_user.get('user_id')
    transaction.updated_at = datetime.utcnow()
    transaction_data = transaction.model_dump(exclude_unset=True)
    session.add(get_transaction.sqlmodel_update(transaction_data))
    session.commit()
    return RestResponse(data = transaction_data, message = f"Transaction Updated sucessfully")


@router.delete('/expense/delete/{transaction_id}')
def transaction_delete(response:Response, session=session, current_user=user, transaction_id:int|None = None):
    get_transaction = session.get(ExpenseModel, transaction_id)
    if not get_transaction:
        response.status_code = 400
        return RestResponse(error="transaction not found")
    
    session.delete(get_transaction)
    session.commit()
    response.status_code = 200
    return RestResponse(message = f"Transaction deleted successfully")


