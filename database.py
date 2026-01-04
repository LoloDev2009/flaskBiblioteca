import sqlite3

db = 'database/books.db'

def tables():
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS libros(
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   portada TEXT,
                   titulo TEXT NOT NULL,
                   autor TEXT NOT NULL,
                   editorial TEXT NOT NULL,
                   año INTEGER,
                   isbn INTEGER UNIQUE)""")
    conn.commit()
    conn.close()

def getBooks():
    books = []
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute("""SELECT id,portada,titulo,autor,editorial,año,isbn FROM libros""")
    response = cursor.fetchall()
    conn.commit()
    conn.close()
    for book in response:
        books.append({
            'id': book[0],
            'portada_url': book[1],
            'titulo':book[2],
            'autor':book[3],
            'editorial':book[4],
            'año':book[5],
            'isbn': book[6]
        })
    return books

def searchBook(isbn):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute("""SELECT id,portada,titulo,autor,editorial,año,isbn FROM libros WHERE isbn = ?""",(isbn,))
    response = cursor.fetchone()
    conn.commit()
    conn.close()
    if response:
        book = {
            'id': response[0],
            'portada': response[1],
            'titulo':response[2],
            'autor':response[3],
            'editorial':response[4],
            'año':response[5],
            'isbn': response[6]
        }
        return book
    else: return

def addBook(portada,isbn, title='-', autor='-', editorial='-', date='-'):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute("""INSERT INTO libros (portada,titulo,autor,editorial,año,   isbn) VALUES (?,?,?,?,?,?)""",(portada,title,autor,editorial,date,isbn))
    conn.commit()
    conn.close()
    return

def deleteBook(isbn):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM libros WHERE isbn = ?", (isbn,))
    conn.commit()
    conn.close()
    return

tables()

