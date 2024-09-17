import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from .extensions import db

DB_FOLDER = "instance"
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'sjhbkhdf jknjdnjkb'
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", f'sqlite:///database.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)


    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app

def create_database(app):
    if not path.exists('website/' + DB_NAME):
        with app.app_context():
            db.create_all()
        print('Created Database!')

# postgresql://food_tracker_db_8l5e_user:vq6LNxTtXEhTcwQqGAWNKG6HcGRQfPJq@dpg-crig0l68ii6s73f34l00-a.oregon-postgres.render.com/food_tracker_db_8l5e
