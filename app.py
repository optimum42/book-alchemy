import os
from flask import Flask, request, render_template, redirect, url_for, flash
from sqlalchemy import or_
from datetime import datetime
from data_models import db, Author, Book

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

# Flask needs a secret key to securely sign the session cookie used for flash messages.
app.secret_key = 'super_secret_library_key'

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
    search_query = request.args.get('search')
    sort_by = request.args.get('sort')

    # base query by joining the author
    query = Book.query.join(Author)

    # search filter (title OR author)
    if search_query:
        search_term = f"%{search_query}%"
        query = query.filter(or_(
            Book.title.ilike(search_term),
            Author.name.ilike(search_term)
        ))

    # sorting filter
    if sort_by == 'title':
        query = query.order_by(Book.title)
    elif sort_by == 'author':
        query = query.order_by(Author.name)

    # execute the query
    books = query.all()

    return render_template('home.html', books=books)


@app.route('/book/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    # get the book by its ID or return 404/405
    book = Book.query.get_or_404(book_id)

    book_title = book.title
    author = book.author

    # delete the book and commit the change
    db.session.delete(book)
    db.session.commit()

    # check if the author has any other books left in the database
    remaining_books_count = Book.query.filter_by(author_id=author.id).count()

    if remaining_books_count == 0:
        # delete the author too!
        db.session.delete(author)
        db.session.commit()
        flash(f"Success! '{book_title}' was deleted. Because they had no "
              f"other books, author '{author.name}' was also removed.")
    else:
        flash(f"Success! The book '{book_title}' was deleted.")

    return redirect(url_for('home'))


@app.route('/author/<int:author_id>/delete', methods=['POST'])
def delete_author(author_id):
    # get the author by its ID or return 404/405
    author = Author.query.get_or_404(author_id)
    author_name = author.name

    # delete ALL books associated with this author first
    Book.query.filter_by(author_id=author_id).delete()

    # now delete the author itself
    db.session.delete(author)
    db.session.commit()

    flash(f"Success! Author '{author_name}' and all of their books "
          f"have been deleted from your library.")
    return redirect(url_for('home'))


@app.route('/book/<int:book_id>')
def book_detail(book_id):
    # Fetch the specific book or return a 404 Not Found error
    book = Book.query.get_or_404(book_id)
    return render_template('book_detail.html', book=book)


@app.route('/author/<int:author_id>')
def author_detail(author_id):
    # Fetch the specific author or return a 404 Not Found error
    author = Author.query.get_or_404(author_id)
    return render_template('author_detail.html', author=author)


# Only run once on empty database
# with app.app_context():
#   db.create_all()

app.run(debug=True, host='0.0.0.0', port=5001)
