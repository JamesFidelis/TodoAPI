from typing import Optional

from fastapi import FastAPI, Depends, HTTPException
import uvicorn
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from pydantic import Field, BaseModel
from auth import get_current_user,get_user_exception

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


class TODO(BaseModel):
    title: str = Field(min_length=1)
    description: Optional[str] = Field(min_length=1)
    priority: int = Field(gt=0, lt=11, description="The value ranges from 1-10")
    complete: bool


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@app.get("/todo/all")
async def read_data(db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    data_model = db.query(models.Todos).all()
    return data_model


@app.get('/todo/{todo_id}')
async def get_todo_id(todo_id: int,
                      user: dict = Depends(get_current_user),
                      db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    todo_model = db.query(models.Todos)\
        .filter(models.Todos.id == todo_id)\
        .filter(models.Todos.owner_id == user.get("user_id"))\
        .first()
    if todo_model is not None:
        return todo_model
    raise http_exception()


@app.post("/todo")
async def create_todo(todo: TODO,
                      user: dict = Depends(get_current_user),
                      db: Session = Depends(get_db)):
    todo_model = models.Todos()
    todo_model.title = todo.title
    todo_model.description = todo.description
    todo_model.priority = todo.priority
    todo_model.complete = todo.complete
    todo_model.owner_id = user.get("user_id")

    db.add(todo_model)
    db.commit()

    return statusResponse(201, 'Task Added Successfully!')


@app.put('/todo/{todo_id}')
async def put_todo(todo_id: int, todo: TODO,
                   user: dict = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    todo_model = db.query(models.Todos)\
        .filter(models.Todos.id == todo_id)\
        .filter(models.Todos.owner_id == user.get("user_id"))\
        .first()

    if todo_model is None:
        raise http_exception()

    todo_model.title = todo.title
    todo_model.description = todo.description
    todo_model.priority = todo.priority
    todo_model.complete = todo.complete
    # todo_model.owner_id = user.get("user_id")

    db.add(todo_model)
    db.commit()

    return statusResponse(201, 'Update Successfull')


@app.delete('/{todo_id}')
async def delete_todo(todo_id: int,
                      user: dict = Depends(get_current_user),
                      db: Session = Depends(get_db)):
    todo_model = db.query(models.Todos)\
        .filter(models.Todos.id == todo_id)\
        .filter(models.Todos.owner_id == user.get("user_id"))\
        .first()

    if todo_model is None:
        raise http_exception()

    db.query(models.Todos).filter(models.Todos.id == todo_id).delete()
    db.commit()

    return statusResponse(201, "Task deleted successfully")


def http_exception():
    return HTTPException(status_code=404, detail="Todo not found")


def statusResponse(status_code: int, response: str):
    return {
        "Status": status_code,
        "response": response
    }


@app.get("/todos/user")
async def read_all_by_user(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None:
        raise HTTPException(status_code=401, detail="user not found")
    todo_model = db.query(models.Todos).filter(models.Todos.owner_id == user.get("user_id")).all()
    return todo_model


# uvicorn.run(app, port=9000)
