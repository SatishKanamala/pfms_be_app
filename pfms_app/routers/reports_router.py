from fastapi import APIRouter,Depends,Response
from sqlmodel import Session,select
from datetime import datetime
from sqlalchemy import func

from models.transactions_model import TransactionModel
from models.accounts_model import AccountModel
from models.categories_model import CategoryModel
from models.budget_model import BudgetModel
from models.goals_model import GoalModel
from models.investments_model import InvestmentModel
from models.users_model import UserModel
from core.db import session
from core.auth import user
from core.std_response import RestResponse

router = APIRouter()


@router.get("/balance")
def get_balance(response: Response, session=session, user=user):

    data = {
        "balance":0,
        "expenses":0,
        "Income":0
    }
    get_all_acc_balance = session.exec(
        select(func.sum(AccountModel.current_balance))
        .where(AccountModel.user == user.get("user_id"))).first()
    
    if get_all_acc_balance:
        data["balance"] += get_all_acc_balance
    
    get_expenses = session.exec(select(func.sum(TransactionModel.amount))
        .where(TransactionModel.user == user.get("user_id"), TransactionModel.transaction_type=="Expenses")).first()
    
    if get_expenses:
        data["expenses"] += get_expenses
        data["balance"] -= get_expenses

    get_income = session.exec(select(func.sum(TransactionModel.amount))
        .where(TransactionModel.user == user.get("user_id"), TransactionModel.transaction_type=="Income")).first()
    
    if get_income:
        data["Income"] += get_income
        data["balance"] += get_income

    return RestResponse(data=data)


@router.get('/recent-transaction')
def get_recent_transactions(session=session, user=user):
    recent_transactions = session.exec(
        select(func.sum(AccountModel.current_balance))
        .where(AccountModel.user == user.get("user_id")))



#Task
@router.get("/task")
def task(session=session, user=user):
    inner_join = session.exec(select(AccountModel, TransactionModel).join(TransactionModel).where(TransactionModel.user==user.get("user_id"))).all()

    left_join =  session.exec(select(AccountModel).join(TransactionModel, isouter=True).where(TransactionModel.user==user.get("user_id"))).all()
    return inner_join