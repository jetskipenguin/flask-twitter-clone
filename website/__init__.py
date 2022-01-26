from flask import Flask
from datetime import timedelta
from os import path
from flask_sqlalchemy import SQLAlchemy

DB_NAME = 'users.sqlite3'
db = SQLAlchemy()

def create_app():
    app = Flask(__name__, static_url_path="", static_folder="static")

    ######### DATABASE CONFIGURATIONS
    app.secret_key = "SJ8SD6SJ28LH5L3B3N2"
    # database path
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    ######### IMAGE CONFIGURATIONS
    # image upload paths
    app.config['ABSOLUTE_IMAGE_UPLOADS'] = 'C:\\Users\\Collin\\Documents\\Python\\flask-site\\website\\static\\images\\uploads'
    app.config['RELATIVE_IMAGE_UPLOADS'] = 'static\\images\\uploads'
    # profile picture filename
    app.config['PROFILE_FILENAME'] = '__PROFILE__.jfif'
    # allowed image formats
    app.config['ALLOWED_IMAGE_EXTENSIONS'] = ['.png', '.jpg', '.jpeg', '.gif', '.jfif']
    # allowed image size
    app.config['ALLOWED_IMAGE_SIZE'] = 0.5 * 1024 * 1024

    ########## LENGTH CONFIGURATIONS
    app.config['BIO_LENGTH'] = 400
    app.config['POST_LENGTH'] = 400
    
    # length of session tokens
    app.permanent_session_lifetime = timedelta(minutes=30)
    
    db.init_app(app)

    # import blueprints
    from .webpages.pages import pages
    from .webpages.home import home

    # register blueprints
    app.register_blueprint(pages, url_prefix='/u/')
    app.register_blueprint(home, url_prefix='/')

    return app

def create_database(app):
    if not path.exists('website/' + DB_NAME):
        with app.app_context():
            db.create_all()
            print('Created database')