from fastapi import APIRouter,Depends,Response
from sqlmodel import Session,select
from datetime import datetime
from sqlalchemy import desc
from sqlalchemy import func

from models.transactions_model import TransactionModel, IncomeModel, ExpenseModel
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
    
    get_expenses = session.exec(select(func.sum(ExpenseModel.amount))
        .where(ExpenseModel.user == user.get("user_id"))).first()
    
    if get_expenses:
        data["expenses"] += get_expenses
        data["balance"] -= get_expenses

    get_income = session.exec(select(func.sum(IncomeModel.amount))
        .where(IncomeModel.user == user.get("user_id"))).first()
    
    if get_income:
        data["Income"] += get_income
        data["balance"] += get_income

    return RestResponse(data=data)



@router.get('/recent-transaction')
def get_recent_transactions(session=session, user=user):
    # Fetch expense transactions
    expense_transactions = session.exec(
        select(
            ExpenseModel.created_at,
            AccountModel.bank_name,
            AccountModel.account_number,
            ExpenseModel.amount
        ).join(AccountModel)
        .where(ExpenseModel.user == user.get("user_id"))
        .order_by(desc(ExpenseModel.id))
        
    ).all()
    expense_transaction_data = [
        {
            "created_at": txn.created_at,
            "bank_name": txn.bank_name,
            "account_number": txn.account_number,
            "amount": txn.amount,
            "type": "Expense"  # Add type field
        }
        for txn in expense_transactions
    ]

    # Fetch income transactions
    income_transactions = session.exec(
        select(
            IncomeModel.created_at,
            AccountModel.bank_name,
            AccountModel.account_number,
            IncomeModel.amount
        ).join(AccountModel)
        .where(IncomeModel.user == user.get("user_id"))
        .order_by(desc(IncomeModel.id))
        
    ).all()
    income_transaction_data = [
        {
            "created_at": txn.created_at,
            "bank_name": txn.bank_name,
            "account_number": txn.account_number,
            "amount": txn.amount,
            "type": "Income"  # Add type field
        }
        for txn in income_transactions
    ]

    # Combine and sort transactions by created_at in descending order
    transactions = sorted(
        expense_transaction_data + income_transaction_data,
        key=lambda x: x["created_at"],
        reverse=True
    )[:5]
    return RestResponse(data=transactions)

@router.get("/transaction-details")
def get_transaction_details(session=session,user=user):
    transaction_details = session.exec(
    select(
        func.sum(ExpenseModel.amount).label('total_expenses'),
        CategoryModel.name.label('category_name'),
        BudgetModel.amount.label('budget_amount')
    )
    .select_from(ExpenseModel)
    .join(BudgetModel, ExpenseModel.category == BudgetModel.category)
    .join(CategoryModel, CategoryModel.id == BudgetModel.category)
    .where(TransactionModel.user == user.get('user_id'))
    .group_by(CategoryModel.name, BudgetModel.amount)
    ).fetchall()

    response_data = []
    for total_expenses,category_name,budget_amount in transaction_details:
        response_data.append({
            "category_name":category_name,
            "actual_amount":budget_amount,
            "spending_amount":total_expenses
        })

    return RestResponse(data=response_data)

    



