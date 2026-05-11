from typing import Annotated
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status
from database import SessionLocal
from services.auth_service import get_current_user
from services import role_service

router = APIRouter(
    prefix='/roles',
    tags=['roles']
)

class RoleBase(BaseModel):
    role: str

class RoleResponse(BaseModel):
    id: int
    role: str

    class Config:
        from_attributes = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=RoleResponse)
def create_role(role: RoleBase, user: user_dependency, db: db_dependency):
    role_service.create_role(role, user, db)

@router.get("/{role_id}", status_code=status.HTTP_200_OK, response_model=RoleResponse)
def read_role(role_id: int, user: user_dependency, db: db_dependency):
    role_service.read_role(role_id, user, db)

@router.delete("/delete/{role_id}", status_code=status.HTTP_200_OK)
def delete_product(role_id: int, user: user_dependency, db: db_dependency):
    role_service.delete_role(role_id, user, db)