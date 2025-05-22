from app import db

class Like(db.Model):
    __tablename__ = 'likes'

    like_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    target_type = db.Column(db.String(20)) # movie, director, genre
    target_value = db.Column(db.String(100))