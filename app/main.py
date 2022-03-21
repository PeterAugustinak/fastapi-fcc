import time
from typing import List

from fastapi import FastAPI, Response, status, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc

from . import schemas
from . import models
from .database import engine, get_db
from .utils import hash


models.Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Welcome to my new API!"}


@app.get("/posts", response_model=List[schemas.PostResponse])
async def get_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return posts


@app.post("/posts", status_code=status.HTTP_201_CREATED,
          response_model=schemas.PostResponse)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db)):
    posted = create(post, models.Post, db)
    return posted


def create(create_obj, model, db):
    new_obj = model(**create_obj.dict())
    db.add(new_obj)
    db.commit()
    db.refresh(new_obj)

    return new_obj


# must be before post/{id} otherwise 'latest' is taken as {id}
@app.get("/posts/latest", response_model=schemas.PostResponse)
def get_latest_post(db: Session = Depends(get_db)):
    latest_post = db.query(models.Post).order_by(desc(models.Post.id)).first()
    if latest_post:
        return latest_post
    post_not_exist(-1)


@app.get("/posts/{id_}", response_model=schemas.PostResponse)
def get_post(id_: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id_).first()
    if post:
        return post
    post_not_exist(id_)


@app.put("/posts/{id_}", status_code=status.HTTP_202_ACCEPTED,
         response_model=schemas.PostResponse)
def update_post(id_: int, updated_post: schemas.PostUpdate,
                db: Session = Depends(get_db)):
    post = update(id_, updated_post, db)
    if post:
        return post
    post_not_exist(id_)


def update(id_, updated_post, db):
    post_query = db.query(models.Post).filter(models.Post.id == id_)
    if post_query.first():
        post_query.update(updated_post.dict(), synchronize_session=False)
        db.commit()
        return updated_post


@app.delete("/posts/{id_}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id_: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id_)
    if post.first():
        post.delete(synchronize_session=False)
        db.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    post_not_exist(id_)


def post_not_exist(id_: int):
    if id_ != -1:
        message = "No posts found."
    else:
        message = f"Post id {id_} not exist!"
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=message)


@app.post("/users", status_code=status.HTTP_201_CREATED,
          response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    hashed_password = hash(user.password)
    user.password = hashed_password
    user = create(user, models.User, db)
    return user
