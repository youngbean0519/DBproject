class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    hashed_password = db.Column(db.String(128), nullable=False)
    notify_by_email = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<User {self.email}>'