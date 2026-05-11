from typing import Annotated
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status
from database import SessionLocal
from services.auth_service import get_current_user
from services import product_service

router = APIRouter(
    prefix='/products',
    tags=['products']
)

class ProductBase(BaseModel):
    product_name: str = Field(min_length=3, max_length=50)
    price: float = Field(gt=0)

class ProductResponse(BaseModel):
    id: int
    product_name: str
    price: float

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

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ProductResponse)
def create_product(product: ProductBase, user: user_dependency, db: db_dependency):
    product_service.create_product(product, user, db)

@router.get("/{product_id}", status_code=status.HTTP_200_OK, response_model=ProductResponse)
def read_product(product_id: int, db: db_dependency):
    product_service.read_product(product_id, db)

@router.put("/update/{product_id}", status_code=status.HTTP_200_OK, response_model=ProductResponse)
def update_product(product_id: int, user: user_dependency, product: ProductBase, db: db_dependency):
    product_service.update_product(product_id, user, product, db)

@router.delete("/delete/{product_id}", status_code=status.HTTP_200_OK)
def delete_product(product_id: int, user: user_dependency, db: db_dependency):
    product_service.delete_product(product_id, user, db)