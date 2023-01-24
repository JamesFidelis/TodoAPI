from fastapi import FastAPI
import uvicorn
from enum import Enum
from typing import Optional

api = FastAPI()

BOOKS = {
    'book_1': {'Title': 'title_one', 'Author': 'author_one'},
    'book_2': {'Title': 'title_two', 'Author': 'author_two'},
    'book_3': {'Title': 'title_three', 'Author': 'author_three'},
    'book_4': {'Title': 'title_four', 'Author': 'author_four'},
    'book_5': {'Title': 'title_five', 'Author': 'author_five'},
    'book_6': {'Title': 'title_six', 'Author': 'author_six'},
}


class Directions(str, Enum):
    north = "north"
    south = "south"
    east = "east"
    west = "west"


@api.get("/")
async def read_all_books(skip_book: Optional[str] = None):
    if skip_book:
        new_books = BOOKS.copy()
        del new_books[skip_book]
        return new_books
    return BOOKS


@api.post("/")
async def add_new_Book(book_title: str, book_author: str):
    current_book_count = 0
    for book in BOOKS:
        if len(BOOKS) > 0:
            x = int(book.split('_')[-1])
            if x > current_book_count:
                current_book_count = x

    BOOKS[f'book_{current_book_count + 1}'] = {'Title': book_title, 'Author': book_author}
    return BOOKS[f'book_{current_book_count + 1}']
@api.put("/")
async def update_book(book_name,book_title,book_author):
    BOOKS[book_name] = {'Title': book_title, 'Author': book_author}
    return BOOKS[book_name]

@api.delete("/")
async def delete_book(book_name):
    new_books = BOOKS.copy()
    del new_books[book_name]
    return new_books



@api.get("/books/mybook")
async def read_fav_book():
    return {
        "Favourite Book": "Da Vinci Code"
    }


@api.get("/{book_id}")
async def read_specific_book(book_id: str):
    return BOOKS[book_id]


@api.get("/books/{book_id}")
async def read_book(book_id: int):
    return {
        "Book ID": book_id
    }


@api.get("/directions/{Direction_name}")
async def direction_name(Direction_name: Directions):
    if Direction_name == Directions.north:
        return {
            "Direction": Direction_name,
            "sub": "Up"
        }
    if Direction_name == Directions.south:
        return {
            "Direction": Direction_name,
            "sub": "Down"
        }
    if Direction_name == Directions.east:
        return {
            "Direction": Direction_name,
            "sub": "Right"
        }
    if Direction_name == Directions.west:
        return {
            "Direction": Direction_name,
            "sub": "Left"
        }


uvicorn.run(api)
