from typing import Optional

from fastapi import FastAPI, Depends, HTTPException
import uvicorn
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from pydantic import Field, BaseModel

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


@app.get("/")
async def read_data(db: Session = Depends(get_db)):
    return db.query(models.Todos).all()


@app.get('/todo/{todo_id}')
async def get_todo_id(todo_id: int, db: Session = Depends(get_db)):
    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
    if todo_model is not None:
        return todo_model
    raise http_exception()


@app.post("/todo")
async def create_todo(todo: TODO, db: Session = Depends(get_db)):
    todo_model = models.Todos()
    todo_model.title = todo.title
    todo_model.description = todo.description
    todo_model.priority = todo.priority
    todo_model.complete = todo.complete

    db.add(todo_model)
    db.commit()

    return statusResponse(201)


@app.put('/{todo_id}')
async def put_todo(todo_id: int, todo: TODO, db: Session = Depends(get_db)):
    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).first()

    if todo_model is None:
        raise http_exception()

    todo_model.title = todo.title
    todo_model.description = todo.description
    todo_model.priority = todo.priority
    todo_model.complete = todo.complete

    db.add(todo_model)
    db.commit()

    return statusResponse(201)


@app.delete('/{todo_id}')
async def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).first()

    if todo_model is None:
        raise http_exception()

    db.query(models.Todos).filter(models.Todos.id == todo_id).delete()
    db.commit()

    return statusResponse(201)


def http_exception():
    return HTTPException(status_code=404, detail="Todo not found")


def statusResponse(status_code: int):
    return {
        "Status": status_code,
        "response": " Task Deleted Successfully"
    }


uvicorn.run(app)
