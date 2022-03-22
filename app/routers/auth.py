from fastapi import Depends, APIRouter
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .. import models
from .. import schemas
from ..database import get_db
from ..utils import invalid_credentials, verify
from .. import oauth2

router = APIRouter(prefix="/login", tags=["Authentication"])

@router.post("/", response_model=schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(),
          db: Session = Depends(get_db)):

    user = db.query(models.User).filter(
        models.User.email == user_credentials.username).first()

    if user:
        if not verify(user_credentials.password, user.password):
            return invalid_credentials()

        access_token = oauth2.create_access_token(data = {"user_id": user.id})
        return {"access_token": access_token, "token_type": "bearer"}

    return invalid_credentials()
