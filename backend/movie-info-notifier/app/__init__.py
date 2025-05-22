from flask import  Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
import os

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    load_dotenv()
    app =  Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    migrate.init_app(app, db)

    from app.routes.auth import auth_bp
    from app.routes.movies import movies_bp
    from app.routes.likes import likes_bp
    from app.routes.watchlist import watchlist_bp
    from app.routes.recommend import recommend_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(movies_bp)
    app.register_blueprint(likes_bp)
    app.register_blueprint(watchlist_bp)
    app.register_blueprint(recommend_bp)
    
    return app