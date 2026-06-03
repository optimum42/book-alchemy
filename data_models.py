from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Author(db.Model):
    __tablename__ = 'authors'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(150), nullable=False)
    birth_date = db.Column(db.Date, nullable=True)
    date_of_death = db.Column(db.Date, nullable=True)

    def __repr__(self):
        """Formal representation for debugging."""
        return f"<Author(id={self.id}, name='{self.name}')>"

    def __str__(self):
        """Readable representation for end-users."""
        return self.name


class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Storing as String preserves leading zeros.
    isbn = db.Column(db.String(13), unique=True, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    publication_year = db.Column(db.Integer, nullable=True)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'),
                          nullable=False)

    # Allow to access the author object directly from a book instance
    author = db.relationship('Author', backref=db.backref('books', lazy=True))

    def __repr__(self):
        """Formal representation for debugging."""
        return f"<Book(id={self.id}, title='{self.title}', isbn='{self.isbn}')>"

    def __str__(self):
        """Readable representation for end-users."""
        return f"'{self.title}' (Published: {self.publication_year})"

