import sqlite3
import os
import sys
import shutil

APP_NAME = "Biblioteca"

def get_db_path():
    # Carpeta AppData\Local\Biblioteca
    base_dir = os.path.join(
        os.environ.get("LOCALAPPDATA", os.getcwd()),
        APP_NAME
    )

    os.makedirs(base_dir, exist_ok=True)

    db_path = os.path.join(base_dir, "books.db")

    # Si la DB no existe, copiar la incluida en el exe
    if not os.path.exists(db_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        bundled_db = os.path.join(base_path, "database", "books.db")
        shutil.copyfile(bundled_db, db_path)

    return db_path

db = get_db_path()

def tables():
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS libros(
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   portada TEXT,
                   titulo TEXT NOT NULL,
                   autor TEXT NOT NULL,
                   editorial TEXT NOT NULL,
                   estado TEXT NOT NULL,
                   comentario TEXT,
                   isbn INTEGER UNIQUE)""")
    conn.commit()
    conn.close()

def getBooks():
    books = []
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute("""SELECT id,portada,titulo,autor,editorial,isbn,estado FROM libros""")
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
            'isbn':book[5],
            'estado': book[6]
        })
    return books

def searchBook(isbn):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute("""SELECT id,portada,titulo,autor,editorial,estado,isbn FROM libros WHERE isbn = ?""",(isbn,))
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
            'estado':response[5],
            'isbn': response[6]
        }
        return book
    else: return

def addBook(portada,isbn, title, autor, editorial, estado):
    try:
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        cursor.execute("""INSERT INTO libros (portada,titulo,autor,editorial,estado,isbn) VALUES (?,?,?,?,?,?)""",(portada,title,autor,editorial,estado,isbn))
        conn.commit()
        conn.close()
        return "Libro agregado correctamente", 200
    except Exception as e: 
        print(e)
        return "Error al agregar el libro", 500  

def deleteBook(isbn):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM libros WHERE isbn = ?", (isbn,))
    conn.commit()
    conn.close()
    return

def editBook(book):
    isbn = book['isbn']
    titulo = book['titulo']
    autor = book['autor']
    editorial = book['editorial']
    estado = book['estado']
    portada = book['portada_url']
    try:
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        cursor.execute("UPDATE libros SET titulo = ?, autor = ?, editorial = ?, estado = ?, portada = ? WHERE isbn = ? ", (titulo,autor,editorial,estado,portada,isbn))
        conn.commit()
        conn.close()
        return "Libro editado correctamente", 200
    except: return "Error al editar el libro",500

tables()

