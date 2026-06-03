import csv
from datetime import datetime
from app import app, db
from data_models import Author, Book


def seed_from_csv(filepath):
    """
    This standalone function seeds the database with csv data
    """
    with app.app_context():
        print(f"Reading data from {filepath}...")

        with open(filepath, mode='r', encoding='utf-8') as file:
            # DictReader automatically uses the first row as dictionary keys
            csv_reader = csv.DictReader(file)

            for row in csv_reader:
                # check if the ISBN already exists
                if Book.query.filter_by(isbn=row['isbn']).first():
                    print(f"Skipping '{row['title']}' - ISBN already exists.")
                    continue

                # check if the Author already exists
                author = Author.query.filter_by(
                    name=row['author_name']).first()

                if not author:
                    birth = None
                    if row['birth_date'].strip():
                        birth = datetime.strptime(row['birth_date'].strip(),
                                                  '%Y-%m-%d').date()

                    death = None
                    if row['death_date'].strip():
                        death = datetime.strptime(row['death_date'].strip(),
                                                  '%Y-%m-%d').date()

                    author = Author(
                        name=row['author_name'],
                        birth_date=birth,
                        date_of_death=death
                    )
                    db.session.add(author)

                year = int(row['publication_year']) if row[
                    'publication_year'].strip() else None

                new_book = Book(
                    title=row['title'],
                    isbn=row['isbn'],
                    publication_year=year,
                    author=author
                )

                db.session.add(new_book)

        db.session.commit()
        print("CSV data successfully imported!")


if __name__ == '__main__':
    seed_from_csv('data/books_data.csv')