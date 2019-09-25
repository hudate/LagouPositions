from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def app_init(app):
    db.init_app(app)
