from fastapi import APIRouter,Depends,Response
from fastapi_pagination import Page, add_pagination, paginate
from sqlmodel import Session,select
from datetime import datetime

from models.investments_model import InvestmentModel
from core.db import session
from core.auth import user
from core.std_response import RestResponse

router = APIRouter()

@router.post('/create')
def investment_create(investment:InvestmentModel, response:Response, session=session, current_user=user):
    investment.user = current_user.get('user_id')
    investment.created_by = current_user.get('user_id')
    session.add(investment)
    session.commit()
    session.refresh(investment)
    response.status_code = 201
    return RestResponse(data = investment, message = f"Investment created Successfully")
    

@router.get('/get/{investment_id}')
def investment_get(response:Response, session=session, current_user=user, investment_id:int|None = None):
    data = session.exec(select(InvestmentModel).where(InvestmentModel.user == current_user.get("user_id"),InvestmentModel.id == investment_id)).first()
    if not data:
        response.status_code = 400
        return RestResponse(error="No data found")
    return RestResponse(data=data)


@router.get('/get_all/')
def investment_list(response:Response, session=session, current_user=user):
    data = session.exec(select(InvestmentModel).where(InvestmentModel.user == current_user.get("user_id"))).all()

    if not data:
        response.status_code = 400
        return RestResponse(error="No data found")
    return RestResponse(data=data)


@router.put('/update/{investment_id}')
def investment_update(investment:InvestmentModel, response:Response, session=session, current_user=user, investment_id:int|None = None):
    get_investment = session.get(InvestmentModel, investment_id)
    if not get_investment:
        response.status_code = 400
        return RestResponse(error="Investment not found")
    
    investment.updated_by = current_user.get('user_id')
    investment.updated_at = datetime.utcnow()
    investment_data = investment.model_dump(exclude_unset=True)
    session.add(get_investment.sqlmodel_update(investment_data))
    session.commit()
    return RestResponse(data = investment_data, message = f"Investment updated sucessfully")


@router.delete('/delete/{investment_id}')
def investment_delete(response:Response, session=session, current_user=user, investment_id:int|None = None):
    get_investment = session.get(InvestmentModel, investment_id)
    if not get_investment:
        response.status_code = 400
        return RestResponse(error="Investment not found")
    
    session.delete(get_investment)
    session.commit()
    response.status_code = 200
    return RestResponse(message = f"Investment deleted successfully")

