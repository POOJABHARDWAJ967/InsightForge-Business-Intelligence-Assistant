from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

@app.get("/")
async def home():
    return {"message": "Hello FastAPI"}

@app.get("/viewbooks")
async def view_books():
    return {"message": "List of books"}

@app.post("/addbook")
async def add_book(book: dict):
    # add book details in DB etc.
    return {"message": "Book added", "book": book}
