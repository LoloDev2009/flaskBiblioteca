from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
import database
import requests
import json
app = Flask(__name__)

@app.route('/')
def mainView():
    return render_template('index.html')

@app.get('/api/libros')
def books():
    books = database.getBooks()
    return books

@app.route('/api/libro', methods = ['POST'])
def searchBook():
    isbn = request.json['isbn']
    #try:
    #Buscar ISBN en Database
    book = database.searchBook(isbn)
    if book:
        libro={
            'isbn':book['isbn'],
            'titulo':book['titulo'],
            'autor':book['autor'],
            'editorial':book['editorial'],
            'año':book['año'],
            'portada_url':book['portada']
        }
        return {'type': 'edit','libro': libro}
    else:
    #Buscar ISBN en API GoogleBooks
        book = requests.get(f'https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}').content
        book = json.loads(book)
        
        if book['totalItems']:
            data = book['items'][0]['volumeInfo']
            try: portada = data['imageLinks']['thumbnail'] 
            except: portada = '-'
            try: title = data['title']
            except: title = '-'
            try:
                authors = str(data['authors']).replace('[','').replace(']','').replace("""'""",'')
                
            except: authors = '-'
            try: publisher = data['publisher'] 
            except: publisher = '-'
            try: publishedDate = data['publishedDate'] 
            except: publishedDate = '-'

            database.addBook(portada,isbn,title,authors, publisher,publishedDate)
            response = {
                'type':'API',
                'title':title
            }
            return response
        else: return {'type': 'manual'}
    #except Exception as e:
    #    print(e)
    #    return {'error': 500}

@app.route('/api/libro/manual', methods = ['POST'])
def addBookManual():
    data = request.json
    if data['isbn']:
        isbn = data['isbn']
    else: isbn = '-'
    if data['portada_url']:
        portada = data['portada_url'] 
    else:portada = ''
    if data['titulo']:
        title = data['titulo']
    else: title = '-'
    if data['autor']:
        authors = data['autor']
    else: authors = '-'
    if data['editorial']:
        publisher = data['editorial'] 
    else: publisher = '-'
    if data['año']:
        publishedDate = data['año'] 
    else: publishedDate = '-'

    database.addBook(portada,isbn,title,authors, publisher,publishedDate)
    response = {
        'status':200,
        'title':title
    }
    return response

if __name__ == '__main__':
    app.run(debug=True)
