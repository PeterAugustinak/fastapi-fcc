from typing import Optional

from fastapi import FastAPI, Response, status, HTTPException
from fastapi import Body
from pydantic import BaseModel
import uvicorn

app = FastAPI()


class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None

post_id = 1
my_posts = [
    {"title": "default str", "content": "default str",
     "published": False, "rating": 1, "id": 0}
]

def find_post(id):
    for post in my_posts:
        if post.get("id") == id:
            return post


def post_not_exist(id: int):
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Post id {id} not exist!")

@app.get("/")
async def root():
    return {"message": "Welcome to my new API!"}


@app.get("/posts")
async def get_posts():
    return my_posts


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(post: Post):
    posted = create(post)
    return {"data": posted}

def create(post):
    global post_id
    posted = post.dict()
    posted.update({"id": post_id})
    post_id += 1
    my_posts.append(posted)


# must be before post/{id} otherwise 'latest' is taken as {id}
@app.get("/posts/latest")
def get_latest_post():
    post = my_posts[-1]
    if post:
        return {"data": post}
    post_not_exist()


@app.get("/posts/{id}")
def get_post(id: int):
    post = find_post(id)
    if post:
        return {"data": post}
    post_not_exist(id)


@app.put("/posts/{id}")
def update_post(id: int, new_post: Post):
    old_post = find_post(id)
    if old_post:
        updated_post = update(old_post, new_post)
        return {"data": updated_post}
    post_not_exist(id)


def update(old_post, new_post):
    new_post = new_post.dict()
    old_post.update(new_post)
    updated_post = find_post(id)
    return updated_post


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    post = find_post(id)
    if post:
        my_posts.remove(post)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    post_not_exist(id)


# if __name__ == "__main__":
#     uvicorn.run(app, port=8070)