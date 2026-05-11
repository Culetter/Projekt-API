from typing import Annotated
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status
from database import get_db
from fastapi.security import OAuth2PasswordRequestForm
from services import auth_service
from routers.users import UserResponse

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

class CreateUserRequest(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    password: str = Field(min_length=4, max_length=72)
    role_id: int = Field(...)

class Token(BaseModel):
    access_token: str
    token_type: str

db_dependency = Annotated[Session, Depends(get_db)]

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
def create_user(create_user_request: CreateUserRequest, db: db_dependency):
    return auth_service.create_user(create_user_request, db)

@router.post("/token", response_model=Token)
def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    return auth_service.login_for_access_token(form_data, db)