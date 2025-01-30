from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, OperationalError
from dotenv import load_dotenv
import uvicorn
import logging

from core.db import create_db_and_tables
from routers.users_router import router as users_router
from routers.categories_router import router as categories_router
from routers.accounts_router import router as accounts_router
from routers.transactions_router import router as transactions_router
from routers.budget_router import router as budget_router
from routers.investments_router import router as investments_router
from routers.goals_router import router as goal_router
from routers.reports_router import router as reports_router


load_dotenv()
create_db_and_tables()

app = FastAPI()


origins = [
    
    "http://localhost:3000",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows frontend requests from these origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Allow all headers
)
app.add_middleware(SessionMiddleware, secret_key="abc")


@app.exception_handler(RequestValidationError)
def request_exception(request:Request, exc:RequestValidationError):
    errors = exc.errors()
    error_details = [{"field": err["loc"], "error": err["msg"]} for err in errors]
    # print(exc) 
    return JSONResponse(
        status_code=400,
        content = {
            "data":None,
            "message":"",
            "error":[{"error": err["msg"].split(',', 1)[1].strip()} if ',' in err["msg"] else err["msg"] for err in errors ]
            }
    )


@app.exception_handler(Exception)
def global_exception(request:Request, exc:Exception):
    return JSONResponse(
        status_code=500,
        content = {
            "data":None,
            "message":"",
            "error":str(exc)
            }
    )

@app.exception_handler(HTTPException)
def global_exception(request:Request, exc:HTTPException):
    return JSONResponse(
        status_code=500,
        content = {
            "data":None,
            "message":"",
            "error":str(exc)
            }
    )


@app.exception_handler(IntegrityError)
async def handle_integrity_error(request: Request, exc: IntegrityError):
    # Extract the error message
    error_message = str(exc.orig)
    print("***************************",error_message)
    
    # Handle Unique Constraint Violation
    if "duplicate key value violates unique constraint" in error_message:
        error_type = "Unique Constraint Violation"
        error_detail = "The value you are trying to insert already exists."
        return JSONResponse(
            status_code=409,  # Conflict status code
            content={
                "data": None,
                "message": error_type,
                "error": error_detail
            }
        )
    
    # Handle Foreign Key Constraint Violation
    elif "a foreign key constraint fails" in error_message:
        error_type = "Foreign Key Constraint Violation"
        error_detail = "This item cannot be deleted because it is linked to other records. Please remove the related records first before deleting this item."
        return JSONResponse(
            status_code=422,  # Unprocessable Entity status code
            content={
                "data": None,
                "message": "",
                "error": error_detail
            }
        )
    
    # Handle Not Null Constraint Violation
    elif "not-null violation" in error_message:
        error_type = "Not Null Constraint Violation"
        error_detail = "A required field cannot be null."
        return JSONResponse(
            status_code=400,  # Bad Request status code
            content={
                "data": None,
                "message": error_type,
                "error": error_detail
            }
        )
    
    # Handle Check Constraint Violation
    elif "check constraint violation" in error_message:
        error_type = "Check Constraint Violation"
        error_detail = "The value does not satisfy the check constraint."
        return JSONResponse(
            status_code=400,  # Bad Request status code
            content={
                "data": None,
                "message": error_type,
                "error": error_detail
            }
        )
    
    # Handle General Integrity Errors
    else:
        error_type = "Integrity Error"
        error_detail = "An integrity error occurred while processing the request."
        return JSONResponse(
            status_code=400,  # Bad Request status code for general errors
            content={
                "data": None,
                "message": error_type,
                "error": error_detail
            }
        )


@app.exception_handler(OperationalError)
async def handle_operational_error(request: Request, exc: OperationalError):
    return JSONResponse(
        status_code=500,
        content={
            "data":None,
            "message":"",
            "error":str(exc)
            }
    )


app.include_router(users_router, prefix="/api/v1/user", tags=["User"])
app.include_router(categories_router, prefix="/api/v1/category", tags=["Category"])
app.include_router(accounts_router, prefix="/api/v1/account", tags=["Account"])
app.include_router(transactions_router, prefix="/api/v1/transaction", tags=["Transaction"])
app.include_router(budget_router, prefix="/api/v1/budget", tags=["Budget"])
app.include_router(investments_router, prefix="/api/v1/investment", tags=["Investment"])
app.include_router(goal_router, prefix="/api/v1/goal", tags=["Goal"])
app.include_router(reports_router, prefix="/api/v1/reports", tags=["Reports"])


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)