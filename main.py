from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uuid
from database import connection, cursor
from datetime import datetime
import pymysql.cursors


app = FastAPI()


templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def authors(request: Request):
    cursor.execute("SELECT * FROM authors")
    authors = cursor.fetchall()
    return templates.TemplateResponse("authors.html", {"request": request, "authors": authors})


@app.post("/authors")
def create_author(name: str = Form(...),email: str = Form(...),date_of_birth: str = Form(...),
):
    # chceck if the email already exists
    cursor.execute("SELECT * FROM authors WHERE email = %s", (email,))
    existing_author = cursor.fetchone()
    if existing_author:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    
    author_id = str(uuid.uuid4())
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        """
        INSERT INTO authors (id, name, email, date_of_birth, created_at)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (author_id, name, email, date_of_birth, created_at),
    )
    if cursor.rowcount == 0:
        raise HTTPException(status_code=500, detail="Failed to create author")
    connection.commit()
    return {"message": "Author created successfully"}

@app.get("/all_authors")
def get_all_authors():
    cursor.execute("SELECT * FROM authors")
    authors = cursor.fetchall()
    return authors

@app.get("/author/{author_id}")
def get_author(author_id: str):
    cursor.execute("SELECT * FROM authors WHERE id = %s", (author_id,))
    author = cursor.fetchone()
    return author

@app.get("/books", response_class=HTMLResponse)
async def books(request: Request):
    # Fetch all books
    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()
    
    # Fetch all authors
    cursor.execute("SELECT * FROM authors")
    authors = cursor.fetchall()
    
    return templates.TemplateResponse("books.html", {"request": request, "books": books, "authors": authors})

@app.post("/books")
async def create_book(title: str = Form(...), author_id: str = Form(...), published_date: str = Form(...), isbn: str = Form(...), quantity: int = Form(...), available_copies: int = Form(...)):
    book_id = str(uuid.uuid4())
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if not author_id:
        raise HTTPException(status_code=400, detail="Author ID is required")
    
    cursor.execute(
        """
        INSERT INTO books (id, title, author_id, published_date, isbn, quantity, available_copies, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (book_id, title, author_id, published_date, isbn, quantity, available_copies, created_at),
    )
    if cursor.rowcount == 0:
        raise HTTPException(status_code=500, detail="Failed to create book")
    connection.commit()
    return {"message": "Book created successfully"}

@app.get("/all_books")
async def get_all_books():
    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()
    return books

@app.get("/book/{book_id}")
async def get_book(book_id: str):
    cursor.execute("SELECT * FROM books WHERE id = %s", (book_id,))
    book = cursor.fetchone()
    return book

@app.get("/borrowers", response_class=HTMLResponse)
async def borrowers(request: Request):
    cursor.execute("SELECT * FROM borrowers")
    borrowers = cursor.fetchall()
    return templates.TemplateResponse("borrowers.html", {"request": request, "borrowers": borrowers})
    
@app.post("/borrowers")
async def create_borrower(name: str = Form(...), email: str = Form(...), membership_date: str = Form(...), phone_number: str = Form(...)):
    
    # check if the email already exists
    cursor.execute("SELECT * FROM borrowers WHERE email = %s", (email,))
    existing_borrower = cursor.fetchone()
    if existing_borrower:
        raise HTTPException(status_code=400, detail="Email already exists")
    borrower_id = str(uuid.uuid4())
    created_at = datetime.now().strftime("%y-%m-%d %H:%M:%S")
    cursor.execute(
        """
        INSERT INTO borrowers (id, name, email, membership_date, phone_number, created_at) VALUES (%s, %s, %s, %s, %s, %s) 
        """,
    (borrower_id, name, email, membership_date, phone_number, created_at)
     )
    if cursor.rowcount == 0:
        raise HTTPException(status_code=500, detail="Failed to create Borrower")
    connection.commit()
    return {"message": "borrower created succesfully"}
        
@app.get("/all_borrowers")
async def get_borrowers():
    cursor.execute("SELECT * FROM borrowers")
    borrowers = cursor.fetchall()
    return borrowers
    
@app.get("/borrowers/{borrower_id}")
async def get_borrower(borrower_id = str):
    cursor.execute("SELECT * FROM borrowers WHERE id = %s" , (borrower_id,))
    borrower = cursor.fetchone()
    return borrower

@app.get("/transactions", response_class= HTMLResponse)
async def transaction(request: Request):
    cursor.execute("SELECT * FROM transactions")
    transactions = cursor.fetchall()
    
    cursor.execute("SELECT * FROM borrowers")
    borrowers = cursor.fetchall()
    
    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()
    return templates.TemplateResponse("transactions.html", {"request": request, "transactions": transactions, "borrowers": borrowers, "books": books})

@app.post("/transactions")
async def create_transaction(borrower_id: str = Form(...), book_id: str = Form(...), transaction_type: str = Form(...), transaction_date: str = Form(...), due_date: str = Form(...), return_date: str = Form(...)):
    transaction_id = str(uuid.uuid4())
    
    if not borrower_id:
        raise HTTPException(status_code=400, detail="Borrower ID is required")
    
    if not book_id:
        raise HTTPException(status_code=400, detail="Book ID is required")
    cursor.execute(
        """
        INSERT INTO transactions (id, borrower_id, book_id, transaction_type, transaction_date, due_date, return_date)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (transaction_id, borrower_id, book_id, transaction_type, transaction_date, due_date, return_date),
    )
    if cursor.rowcount == 0:
        raise HTTPException(status_code=500, detail="Failed to create transaction")
    connection.commit()
    return {"message": "transaction created successfully"}
    
@app.get("/all_transactions")
async def get_all_transactions():
    cursor.execute("SELECT * FROM transactions")
    transactions = cursor.fetchall()
    return transactions

@app.get("/transactions/{trasnaction_id}")
async def get_transaction(transaction_id: str):
    cursor.execute("SELECT * FROM transactions WHERE id = %s", (transaction_id,))
    transaction = cursor.fetchone()
    return transaction

@app.get("/borrowers/{borrower_id}/transactions")
async def get_borrower_transactions(borrower_id: str):
    cursor.execute("SELECT * FROM transactions WHERE borrower_id = %s", (borrower_id,))
    transactions = cursor.fetchall()
    return transactions
    

# Ensure the connection is properly closed on exit
import atexit

def close_connection():
    cursor.close()
    connection.close()

atexit.register(close_connection)
