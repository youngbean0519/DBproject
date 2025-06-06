from flask import  Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
import os
# 개발자 모드 용
from flask_cors import CORS

env = os.getenv('FLASK_ENV', 'development')

print(f"현재 모드: {env}")

if env == 'production':
    load_dotenv('.env.production')
else:
    load_dotenv('.env.development')

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app =  Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    migrate.init_app(app, db)

    # 개발자 용 CORS 설정
    CORS(app, supports_credentials=True)

    from app import models
    from app.routes.auth import auth_bp
    from app.routes.movies import movies_bp
    from app.routes.likes import likes_bp
    from app.routes.watchlist import watchlist_bp
    from app.routes.recommend import recommend_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(movies_bp)
    app.register_blueprint(likes_bp)
    app.register_blueprint(watchlist_bp)
    app.register_blueprint(recommend_bp)
    app.register_blueprint(admin_bp)
    
    return app