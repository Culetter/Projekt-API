from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from starlette import status
import models

def create_order(order, user, db):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")

    db_order = models.Order(user_id=user.get("id"))

    db.add(db_order)
    db.flush()

    product_ids = [item.product_id for item in order.items]
    products = db.query(models.Product).filter(models.Product.id.in_(product_ids)).all()
    product_map = {p.id: p for p in products}

    missing = set(product_ids) - product_map.keys()
    if missing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product not found: {list(missing)}")

    db_order.items = [models.OrderItem(product_id=item.product_id, quantity=item.quantity) for item in order.items]

    db.commit()
    db.refresh(db_order)

    total_price = sum(item.quantity * product_map[item.product_id].price for item in order.items)

    return {
        "id": db_order.id,
        "user": db_order.user,
        "items": db_order.items,
        "total_price": total_price
    }

def read_order(order_id, user, db):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")

    db_order = db.query(models.Order).options(joinedload(models.Order.user), joinedload(models.Order.items).joinedload(models.OrderItem.product)).filter(models.Order.id == order_id).first()
    if db_order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    if user.get("role") == "client" and user.get("id") != db_order.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    
    total_price = sum(item.quantity * item.product.price for item in db_order.items)
    return {
        "id": db_order.id,
        "user": db_order.user,
        "items": db_order.items,
        "total_price": total_price
    }


def update_order(order_id, order, user, db):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    
    if user.get("role") == "client":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    order_db = db.query(models.Order).options(joinedload(models.Order.user), joinedload(models.Order.items).joinedload(models.OrderItem.product)).filter(models.Order.id == order_id).first()
    if order_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    for field, value in order.model_dump().items():
        setattr(order_db, field, value)
    
    db.commit()
    db.refresh(order_db)

    return order_db

def delete_order(order_id, user, db):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    
    if user.get("role") == "client":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    db_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if db_order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    db.delete(db_order)
    db.commit()
    
    return {"Message": "Order deleted!"}