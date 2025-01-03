from fastapi import APIRouter,Depends,Response
from sqlmodel import Session,select
from datetime import datetime

from models.budget_model import BudgetModel
from core.db import session
from core.auth import user
from core.std_response import RestResponse

router = APIRouter()

@router.post('/create')
def budget_create(budget:BudgetModel, response:Response, session=session, current_user=user):
    budget.user = current_user.get('user_id')
    budget.created_by = current_user.get('user_id')
    session.add(budget)
    session.commit()
    session.refresh(budget)
    response.status_code = 201
    return RestResponse(data = budget, message = f"Budget created Successfully")
    

@router.get('/get/{budget_id}')
def budget_get(response:Response, session=session, current_user=user, budget_id:int|None = None):
    data = session.exec(select(BudgetModel).where(BudgetModel.user == current_user.get("user_id"),BudgetModel.id == budget_id)).first()
    if not data:
        response.status_code = 400
        return RestResponse(error="No data found")
    return RestResponse(data=data)


@router.get('/get_all/')
def budget_list(response:Response, session=session, current_user=user):
    data = session.exec(select(BudgetModel).where(BudgetModel.user == current_user.get("user_id"))).all()
    if not data:
        response.status_code = 400
        return RestResponse(error="No data found")
    return RestResponse(data=data)


@router.put('/update/{budget_id}')
def budget_update(budget:BudgetModel, response:Response, session=session, current_user=user, budget_id:int|None = None):
    get_budget = session.get(BudgetModel, budget_id)
    if not get_budget:
        response.status_code = 400
        return RestResponse(error="Budget not found")
    
    budget.updated_by = current_user.get('user_id')
    budget.updated_at = datetime.utcnow()
    budget_data = budget.model_dump(exclude_unset=True)
    session.add(get_budget.sqlmodel_update(budget_data))
    session.commit()
    return RestResponse(data = budget_data, message = f"Budget updated sucessfully")


@router.delete('/delete/{budget_id}')
def budget_delete(response:Response, session=session, current_user=user, budget_id:int|None = None):
    get_budget = session.get(BudgetModel, budget_id)
    if not get_budget:
        response.status_code = 400
        return RestResponse(error="Budget not found")
    
    session.delete(get_budget)
    session.commit()
    response.status_code = 200
    return RestResponse(message = f"Budget deleted successfully")

