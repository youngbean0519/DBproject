from app import db

class User(db.model):
    __tablename__ = 'users'
    use_id = db.Column(db.Integer, primary_key=True)
    email = db.column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    notify_by_email = db.Column(db.Boolean, default=True)