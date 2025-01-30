from fastapi import APIRouter,Depends,Response
from sqlmodel import Session,select
from datetime import datetime

from models.categories_model import CategoryModel
from core.db import session
from core.auth import user
from core.std_response import RestResponse

router = APIRouter()

@router.post('/create')
def category_create(category:CategoryModel, response:Response, session=session, current_user=user):
    user_category = session.exec(select(CategoryModel).where(CategoryModel.name == category.name.capitalize(),CategoryModel.user == current_user.get('user_id'))).first()
    if user_category:
        response.status_code = 400
        return RestResponse(error=f'{category.name} is already exists.')
    category.user = current_user.get('user_id')
    category.created_by = current_user.get('user_id')
    category.name = category.name.capitalize()
    session.add(category)
    session.commit()
    session.refresh(category)
    response.status_code = 201
    return RestResponse(data = category, message = f"{category.name} created Successfully")
    

@router.get('/get/{category_id}')
def category_get(response:Response, session=session, current_user=user, category_id:int|None = None):
    data = session.exec(select(CategoryModel).where(CategoryModel.user == current_user.get("user_id"),CategoryModel.id == category_id)).first()
    if not data:
        response.status_code = 400
        return RestResponse(error="No data found")
    return RestResponse(data=data)


@router.get('/get_all/')
def category_list(response:Response, session=session, current_user=user):
    data = session.exec(select(CategoryModel).where(CategoryModel.user == current_user.get("user_id"))).all()
    if not data:
        response.status_code = 400
        return RestResponse(error="No data found")
    return RestResponse(data=data)


@router.put('/update/{category_id}')
def category_update(category:CategoryModel, response:Response, session=session, current_user=user, category_id:int|None = None):
    get_category = session.get(CategoryModel, category_id)
    if not get_category:
        response.status_code = 400
        return RestResponse(error="Category not found")
    
    category.updated_by = current_user.get('user_id')
    category.updated_at = datetime.utcnow()
    category_data = category.model_dump(exclude_unset=True)
    session.add(get_category.sqlmodel_update(category_data))
    session.commit()
    return RestResponse(data = category_data, message = f"{category.name} Updated sucessfully")


@router.delete('/delete/{category_id}')
def category_delete(response:Response, session=session, current_user=user, category_id:int|None = None):
    get_category = session.get(CategoryModel, category_id)
    if not get_category:
        response.status_code = 400
        return RestResponse(error="Category not found")
    
    session.delete(get_category)
    session.commit()
    response.status_code = 200
    return RestResponse(message = f"{get_category.name} deleted successfully")

