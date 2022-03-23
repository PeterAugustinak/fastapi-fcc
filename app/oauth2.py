from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from . import database
from . import  schemas
from . import models

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')


SECRET_KEY = "jkhjk2423423423jhk234234kjh234k23h4k234knkcfccg23423"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme),
                     db: Session = Depends(database.get_db)):
    detail = "Could not validate credentials"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail=detail,
        headers={"WWW-Authenticate": "Bearer"})

    token = verify_access_token(token, credentials_exception)
    user = db.query(models.User).filter(models.User.id == token.id).first()

    return user


def verify_access_token(token: str, credential_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, [ALGORITHM])
        id_: str = payload.get("user_id")

        if not id_:
            raise credential_exception
        token_data = schemas.TokenData(id=id_)
    except JWTError:
        raise credential_exception

    return token_data
