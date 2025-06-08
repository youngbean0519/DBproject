from app import db

class Watchlist(db.Model):
    __tablename__ = 'watchlist'

    watch_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    movie_id = db.Column(db.String(50))
    movie_title = db.Column(db.String(200))
    director = db.Column(db.String(100))
    genre = db.Column(db.String(50))
    actors = db.Column(db.Text)
    country = db.Column(db.String(50))
    movie_type = db.Column(db.String(50))
    release_date = db.Column(db.Date)