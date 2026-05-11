from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from starlette import status
from models import Product

def create_product(product, user, db):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    
    if user.get("role") == "client":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    
    try:
        db_product = Product(**product.model_dump())

        db.add(db_product)
        db.commit()
        db.refresh(db_product)

        return db_product
    except IntegrityError:
        db.rollback()

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Product alredy exists")

def read_product(product_id, db):
    product = db.query(Product).filter(Product.id == product_id).first()

    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    return product

def update_product(product_id, user, product, db):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    if user.get("role") == "client":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    db_product = db.query(Product).filter(Product.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    for field, value in product.model_dump().items():
        setattr(db_product, field, value)
    
    db.commit()
    db.refresh(db_product)
    return db_product

def delete_product(product_id, user, db):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    
    if user.get("role") == "client":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    db_product = db.query(Product).filter(Product.id == product_id).first()

    if db_product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    db.delete(db_product)
    db.commit()
    return {"Message": "Product deleted"}
