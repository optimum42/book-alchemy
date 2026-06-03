import os
from flask import Flask, request, render_template
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from data_models import db, Author, Book

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config[
    'SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/library.sqlite')}"

db.init_app(app)


@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    message = None  # Holds the success message, if any

    if request.method == 'POST':
        # Get the data from the submitted form
        name = request.form.get('name')
        birth_date_str = request.form.get('birthdate')
        date_of_death_str = request.form.get('date_of_death')

        birth_date = None
        if birth_date_str:
            birth_date = datetime.strptime(birth_date_str,
                                           '%Y-%m-%d').date()

        date_of_death = None
        if date_of_death_str:
            date_of_death = datetime.strptime(date_of_death_str,
                                              '%Y-%m-%d').date()

        new_author = Author(
            name=name,
            birth_date=birth_date,
            date_of_death=date_of_death
        )

        db.session.add(new_author)
        db.session.commit()

        message = f"Success! Author '{name}' has been added to the database."

    return render_template('add_author.html', message=message)


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    message = None

    # Fetch all authors from the database for the dropdown menu
    authors = Author.query.all()

    if request.method == 'POST':
        title = request.form.get('title')
        isbn = request.form.get('isbn')
        publication_year_str = request.form.get('publication_year')
        author_id = request.form.get('author_id')

        publication_year = None
        if publication_year_str:
            publication_year = int(publication_year_str)

        new_book = Book(
            title=title,
            isbn=isbn,
            publication_year=publication_year,
            author_id=author_id
        )

        db.session.add(new_book)
        db.session.commit()

        message = f"Success! The book '{title}' has been added."

    return render_template('add_book.html',
                           authors=authors, message=message)


@app.route('/')
def home():
    # Alle Bücher aus der Datenbank abfragen
    books = Book.query.all()

    # Das Template rendern und die Liste der Bücher übergeben
    return render_template('home.html', books=books)


# Only run once on empty database
# with app.app_context():
#   db.create_all()

app.run(debug=True, host='0.0.0.0', port=5001)
