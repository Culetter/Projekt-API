from typing import Annotated
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status
from database import SessionLocal
from routers.products import ProductResponse
from routers.users import UserResponse
from services.auth_service import get_current_user
from services import order_service

router = APIRouter(
    prefix='/orders',
    tags=['orders']
)

class OrderItemsBase(BaseModel):
    product_id: int = Field(...)
    quantity: int = Field(default=1)

class OrderItemsResponse(BaseModel):
    id: int
    product: ProductResponse
    quantity: int

    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    status: str = Field(default="pending")
    items: list[OrderItemsBase] = Field(...)

class OrderResponse(BaseModel):
    id: int
    user: UserResponse
    items: list[OrderItemsResponse]
    total_price: float

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

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=OrderResponse)
def create_order(order: OrderBase, user: user_dependency, db: db_dependency):
    order_service.create_order(order, user, db)

@router.get("/{order_id}", status_code=status.HTTP_200_OK, response_model=OrderResponse)
def read_order(order_id: int, user: user_dependency, db: db_dependency):
    order_service.read_order(order_id, user, db)

@router.put("/update/{order_id}", status_code=status.HTTP_200_OK, response_model=OrderResponse)
def update_order(order_id: int, order: OrderBase, user: user_dependency, db: db_dependency):
    order_service.update_order(order_id, order, user, db)

@router.delete("/delete/{order_id}", status_code=status.HTTP_200_OK)
def delete_order(order_id: int, user: user_dependency, db: db_dependency):
    order_service.delete_order(order_id, user, db)
