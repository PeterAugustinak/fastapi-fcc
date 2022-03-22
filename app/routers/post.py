from typing import List

from fastapi import Response, status, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import desc

from .. import schemas
from .. import oauth2
from .. import models
from ..database import get_db
from ..utils import record_not_exist, create


router = APIRouter(prefix="/posts", tags=["Posts"])


@router.get("/", response_model=List[schemas.PostResponse])
async def get_posts(db: Session = Depends(get_db),
                    current_user: int = Depends(oauth2.get_current_user)):
    print(current_user.email)
    posts = db.query(models.Post).all()
    return posts


@router.post("/", status_code=status.HTTP_201_CREATED,
          response_model=schemas.PostResponse)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db),
                current_user: int = Depends(oauth2.get_current_user)):
    posted = create(post, models.Post, db)
    return posted


# must be before post/{id} otherwise 'latest' is taken as {id}
@router.get("/latest", response_model=schemas.PostResponse)
def get_latest_post(db: Session = Depends(get_db)):
    latest_post = db.query(models.Post).order_by(desc(models.Post.id)).first()
    if latest_post:
        return latest_post
    record_not_exist("post", -1)


@router.get("/{id_}", response_model=schemas.PostResponse)
def get_post(id_: int, db: Session = Depends(get_db),
             current_user: int = Depends(oauth2.get_current_user)):
    post = db.query(models.Post).filter(models.Post.id == id_).first()
    if post:
        return post
    record_not_exist("post", id_)


@router.put("/{id_}", status_code=status.HTTP_202_ACCEPTED,
         response_model=schemas.PostResponse)
def update_post(id_: int, updated_post: schemas.PostUpdate,
                db: Session = Depends(get_db),
                current_user: int = Depends(oauth2.get_current_user)):
    post = update(id_, updated_post, db)
    if post:
        return post
    record_not_exist("post", id_)


def update(id_, updated_post, db):
    post_query = db.query(models.Post).filter(models.Post.id == id_)
    post = post_query.first()
    if post:
        post_query.update(updated_post.dict(), synchronize_session=False)
        db.commit()
        return post


@router.delete("/{id_}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id_: int, db: Session = Depends(get_db),
                current_user: int = Depends(oauth2.get_current_user)):
    post = db.query(models.Post).filter(models.Post.id == id_)
    if post.first():
        post.delete(synchronize_session=False)
        db.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    record_not_exist("post", id_)