from fastapi import APIRouter,Depends,Response
from sqlmodel import Session,select
from datetime import datetime

from models.goals_model import GoalModel
from core.db import session
from core.auth import user
from core.std_response import RestResponse

router = APIRouter()

@router.post('/create')
def goal_create(goal:GoalModel, response:Response, session=session, current_user=user):
    goal.user = current_user.get('user_id')
    goal.created_by = current_user.get('user_id')
    session.add(goal)
    session.commit()
    session.refresh(goal)
    response.status_code = 201
    return RestResponse(data = goal, message = f"{goal.goal_name} goal created Successfully")
    

@router.get('/get/{goal_id}')
def goal_get(response:Response, session=session, current_user=user, goal_id:int|None = None):
    data = session.exec(select(GoalModel).where(GoalModel.user == current_user.get("user_id"),GoalModel.id == goal_id)).first()
    if not data:
        response.status_code = 400
        return RestResponse(error="No data found")
    return RestResponse(data=data)


@router.get('/get_all/')
def goal_list(response:Response, session=session, current_user=user):
    data = session.exec(select(GoalModel).where(GoalModel.user == current_user.get("user_id"))).all()
    if not data:
        response.status_code = 400
        return RestResponse(error="No data found")
    return RestResponse(data=data)


@router.put('/update/{goal_id}')
def goal_update(goal:GoalModel, response:Response, session=session, current_user=user, goal_id:int|None = None):
    get_goal = session.get(GoalModel, goal_id)
    if not get_goal:
        response.status_code = 400
        return RestResponse(error="Goal not found")
    
    goal.updated_by = current_user.get('user_id')
    goal.updated_at = datetime.utcnow()
    goal_data = goal.model_dump(exclude_unset=True)
    session.add(get_goal.sqlmodel_update(goal_data))
    session.commit()
    return RestResponse(data = goal_data, message = f"{goal.goal_name} goal updated sucessfully")


@router.delete('/delete/{goal_id}')
def goal_delete(response:Response, session=session, current_user=user, goal_id:int|None = None):
    get_goal = session.get(GoalModel, goal_id)
    if not get_goal:
        response.status_code = 400
        return RestResponse(error="goal not found")
    
    session.delete(get_goal)
    session.commit()
    response.status_code = 200
    return RestResponse(message = f"{get_goal.goal_name} goal deleted successfully")

