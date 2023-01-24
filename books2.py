import starlette.status
from fastapi import FastAPI, HTTPException, status, Form, Header
import uvicorn
from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional

from starlette.requests import Request
from starlette.responses import JSONResponse

api = FastAPI()


class NegativeNumberException(Exception):
    def __init__(self, books_to_return):
        self.books_to_return = books_to_return


class Books(BaseModel):
    id: UUID
    title: str = Field(min_length=1)
    author: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(min_length=1,
                                       max_length=100,
                                       title='Book description')
    rating: int = Field(gt=-1, lt=101)

    class Config:
        schema_extra = {
            "example": {
                "id": "1fa85f64-5717-4562-b3fc-2c963f66afa6",
                "title": "Sample Title",
                "author": "Sample Author",
                "description": "Sample description",
                "rating": 40,
            }
        }


class BookNoRating(BaseModel):
    id: UUID
    title: str = Field(min_length=1)
    author: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(min_length=1,
                                       max_length=100,
                                       title='Book description')


BOOKS = []


@api.post('/books/login')
async def book_login(username: str = Form(...), password: str = Form(...)):
    return {
        "username": username,
        "password": password
    }


@api.get('/header')
async def random_headers(random_header:str = Header(...)):
    return {"Random header": random_header}


@api.exception_handler(NegativeNumberException)
async def negative_number_exception(request: Request,
                                    exception: NegativeNumberException):
    return JSONResponse(status_code=414,
                        content={
                            "message": f"You cannot have {exception.books_to_return} books! Please try again."
                        })


@api.get("/")
async def read_all_books(books_to_return: Optional[int] = None):
    if books_to_return and books_to_return < 0:
        raise NegativeNumberException(books_to_return=books_to_return)

    if len(BOOKS) == 0:
        static_books()
    if books_to_return is not None:
        newbooks = []
        i = 1
        if len(BOOKS) > books_to_return > 0:
            while i <= books_to_return:
                newbooks.append(BOOKS[i + 1])
                i += 1
            return newbooks

    return BOOKS


@api.get("/rating", response_model=BookNoRating)
async def read_no_rating_books(books_to_return: Optional[int] = None):
    if books_to_return and books_to_return < 0:
        raise NegativeNumberException(books_to_return=books_to_return)

    if len(BOOKS) == 0:
        static_books()
    if books_to_return is not None:
        newbooks = []
        i = 1
        if len(BOOKS) > books_to_return > 0:
            while i <= books_to_return:
                newbooks.append(BOOKS[i + 1])
                i += 1
            return newbooks

    return BOOKS


@api.post("/", status_code=status.HTTP_201_CREATED)
async def create_book(book: Books):
    BOOKS.append(book)
    return book


@api.get('/book/{book_id}')
async def get_by_book(book_id: UUID):
    for x in BOOKS:
        if x.id == book_id:
            return x
    raise exception()


@api.get('/book/rating/{book_id}', response_model=BookNoRating)
async def get_no_rating_book(book_id: UUID):
    for x in BOOKS:
        if x.id == book_id:
            return x
    raise exception()


@api.put("/{book_id}")
async def change_book(book_id: UUID, book: Books):
    counter = 0
    for x in BOOKS:
        counter += 1
        if x.id == book_id:
            BOOKS[counter - 1] = book
            return BOOKS[counter - 1]
    raise exception()


@api.delete("/{book_id}")
async def delete_book(book_id: UUID):
    counter = 0
    for x in BOOKS:
        counter += 1
        if x.id == book_id:
            del BOOKS[counter - 1]
            return f'ID: {book_id} deleted'
    raise exception()


def static_books():
    book_1 = Books(
        id="1fa85f64-5717-4562-b3fc-2c963f66afa6",
        title="Book 1",
        author=" Author 1",
        description="Description 1",
        rating=40,
    )
    book_2 = Books(
        id="1fa85f64-5717-4522-b3fc-2c963f66afa6",
        title="Book 2",
        author=" Author 2",
        description="Description 2",
        rating=40,
    )
    book_3 = Books(
        id="1fa85f64-5717-4592-b3fc-2c963f66afa6",
        title="Book 3",
        author=" Author 3",
        description="Description 3",
        rating=40,
    )
    book_4 = Books(
        id="1fa85f64-5717-4542-b3fc-2c963f66afa6",
        title="Book 4",
        author=" Author 4",
        description="Description 4",
        rating=40,
    )

    BOOKS.append(book_1)
    BOOKS.append(book_2)
    BOOKS.append(book_3)
    BOOKS.append(book_4)


def exception():
    return HTTPException(status_code=404,
                         detail="Not found")


uvicorn.run(api)
