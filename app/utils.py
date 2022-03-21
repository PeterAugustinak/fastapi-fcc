# Util functions

from passlib.context import CryptContext
from fastapi import status, HTTPException


def hash(password: str):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed_password = pwd_context.hash(password)
    return hashed_password


def record_not_exist(id_: int, obj):
    if id_ != -1:
        message = f"No {obj}s found."
    else:
        message = f"{obj} id {id_} not exist!"
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=message)