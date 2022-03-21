from fastapi import status, Depends, APIRouter
from sqlalchemy.orm import Session

from .. import schemas
from .. import models
from ..database import get_db
from ..utils import hash, record_not_exist, create


router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", status_code=status.HTTP_201_CREATED,
          response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    hashed_password = hash(user.password)
    user.password = hashed_password
    user = create(user, models.User, db)
    return user


@router.get("/{id_}", response_model=schemas.UserResponse)
def get_user(id_: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id_).first()
    if user:
        return user

    record_not_exist(id_, "user")
