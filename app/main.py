import time

from fastapi import FastAPI, Response, status, HTTPException
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor


app = FastAPI()


class Post(BaseModel):
    title: str
    content: str
    published: bool = True


while True:
    try:
        conn = psycopg2.connect(host="localhost", port='5433',
                                database='fastapi',
                                user='postgres', password='password',
                                cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        break
    except Exception as error:
        print("Connection to DB failed")
        print(f"Error: {error}")
        time.sleep(3)


post_id = 1
my_posts = [
    {"title": "default str", "content": "default str",
     "published": False, "rating": 1, "id": 0}
]


def find_post(id_):
    for post in my_posts:
        if post.get("id") == id_:
            return post


def post_not_exist(id_: int):
    if id_ != -1:
        message = "No posts found."
    else:
        message = f"Post id {id_} not exist!"
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=message)


@app.get("/")
async def root():
    return {"message": "Welcome to my new API!"}


@app.get("/posts")
async def get_posts():
    cursor.execute("""SELECT * FROM posts;""")
    posts = cursor.fetchall()
    return posts


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(post: Post):
    posted = create(post)
    return {"data": posted}


def create(post):
    global post_id
    cursor.execute("""INSERT INTO posts (title, content, published) 
                   VALUES (%s, %s, %s) RETURNING * """,
                   (post.title, post.content, post.published))
    conn.commit()
    posted = cursor.fetchone()
    return posted


# must be before post/{id} otherwise 'latest' is taken as {id}
@app.get("/posts/latest")
def get_latest_post():
    cursor.execute("""SELECT * FROM posts ORDER BY created_at DESC LIMIT 1""")
    latest_post = cursor.fetchone()
    if latest_post:
        return {"data": latest_post}
    post_not_exist(-1)


@app.get("/posts/{id_}")
def get_post(id_: int):
    cursor.execute("""SELECT * FROM posts WHERE id = %s""", (str(id_)))
    post = cursor.fetchone()
    if post:
        return {"data": post}
    post_not_exist(id_)


@app.put("/posts/{id_}")
def update_post(id_: int, updated_post: Post):
    cursor.execute("""UPDATE posts SET title = %s, content = %s, 
    published = %s WHERE id = %s RETURNING *""",
                   (updated_post.title, updated_post.content,
                    updated_post.published, str(id_),))
    conn.commit()
    updated_post = cursor.fetchone()
    if updated_post:
        return {"data": updated_post}
    post_not_exist(id_)


def update(old_post, new_post):
    new_post = new_post.dict()
    old_post.update(new_post)
    updated_post = find_post(id)
    return updated_post


@app.delete("/posts/{id_}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id_: int):
    cursor.execute("""DELETE FROM posts WHERE id = %s returning *""",
                   (str(id_),))
    conn.commit()
    deleted_post = cursor.fetchone()
    if deleted_post:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    post_not_exist(id_)


# if __name__ == "__main__":
#     uvicorn.run(app, port=8070)
