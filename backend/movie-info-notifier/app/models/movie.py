from app import db

class Movie(db.Model):
    __tablename__ = 'movies'

    movie_id = db.Column(db.String(50), primary_key=True)
    title = db.Column(db.String(200))
    director = db.Column(db.String(100))
    genre = db.Column(db.String(50))
    actors = db.Column(db.Text)
    country = db.Column(db.String(50))
    movie_type = db.Column(db.String(50))
    release_date = db.Column(db.Date)