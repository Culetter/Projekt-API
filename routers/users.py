from typing import Annotated
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status
from database import get_db
from routers.roles import RoleResponse
from services.auth_service import get_current_user
from services import user_service

router = APIRouter(
    prefix='/users',
    tags=['users']
)

class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    role_id: int = Field(...)

class UserResponse(BaseModel):
    id: int
    username: str
    role: RoleResponse

    class Config:
        from_attributes = True

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get("/{user_id}", status_code=status.HTTP_200_OK, response_model=UserResponse)
def read_user(user_id: int, user: user_dependency, db: db_dependency):
    return user_service.read_user(user_id, user, db)

@router.put("/{user_id}", status_code=status.HTTP_200_OK, response_model=UserResponse)
def update_user(user_id: int, user: UserBase, user_dep: user_dependency, db: db_dependency):
    return user_service.update_user(user_id, user, user_dep, db)

@router.delete("/{user_id}")
def delete_user(user_id: int, user: user_dependency, db: db_dependency):
    return user_service.delete_user(user_id, user, db)