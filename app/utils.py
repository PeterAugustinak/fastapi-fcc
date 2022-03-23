# Util functions

from passlib.context import CryptContext
from fastapi import status, HTTPException

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash(password: str):
    hashed_password = pwd_context.hash(password)
    return hashed_password


def verify(login_password, hashed_password):
    return pwd_context.verify(login_password, hashed_password)


def record_not_exist(obj: str, id_):
    if id_ == -1:
        message = f"No {obj}s found."
    else:
        message = f"{obj} id {id_} not exist!"
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=message)

def invalid_credentials():
    message = f"Invalid Credentials"
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                        detail=message)


def create(create_obj, model, db):
    if type(create_obj) != dict:
        create_obj = create_obj.dict()
    new_obj = model(**create_obj)
    db.add(new_obj)
    db.commit()
    db.refresh(new_obj)

    return new_obj