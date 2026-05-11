from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from starlette import status
from models import Role

def create_role(role, user, db):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    
    if user.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    
    try:
        db_role = Role(**role.model_dump())

        db.add(db_role)
        db.commit()
        db.refresh(db_role)

        return db_role
    except IntegrityError:
        db.rollback()

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role alredy exists")

def read_role(role_id, user, db):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    
    if user.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    db_role = db.query(Role).filter(Role.id == role_id).first()

    if db_role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    
    return db_role

def delete_role(role_id, user, db):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    
    if user.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    db_role = db.query(Role).filter(Role.id == role_id).first()

    if db_role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    
    db.delete(db_role)
    db.commit()
    
    return {"Message": "Role deleted"}