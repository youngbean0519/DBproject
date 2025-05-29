from app import db

class Recommendation(db.Model):
    __tablename__ = 'recommendations'

    rec_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    movie_id = db.Column(db.String(50))
    reason = db.Column(db.Text)