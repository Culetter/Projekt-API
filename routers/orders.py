from typing import Annotated
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status
from database import get_db
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
    status: str
    items: list[OrderItemsResponse]
    total_price: float

    class Config:
        from_attributes = True

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=OrderResponse)
def create_order(order: OrderBase, user: user_dependency, db: db_dependency):
    return order_service.create_order(order, user, db)

@router.get("/{order_id}", status_code=status.HTTP_200_OK, response_model=OrderResponse)
def read_order(order_id: int, user: user_dependency, db: db_dependency):
    return order_service.read_order(order_id, user, db)

@router.delete("/{order_id}", status_code=status.HTTP_200_OK)
def delete_order(order_id: int, user: user_dependency, db: db_dependency):
    return order_service.delete_order(order_id, user, db)
