from authlib.integrations.flask_client import OAuth
from celery.schedules import crontab
from flask import Flask
from flask_admin import Admin
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_admin.contrib.sqla import ModelView
from flask_pymongo import PyMongo
from flask_caching import Cache

from .celery_app import celery_init_app

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
oauth = OAuth()
migrate = Migrate()
admin = Admin()
mongo = PyMongo()
cache = Cache()


def create_app(_config):
    app = Flask(__name__)
    app.config.from_object(_config)

    from app.scrapers import scraper_manager

    app.config.from_mapping(
        CELERY=dict(
            broker_url="redis://localhost",
            result_backend="redis://localhost",
            task_ignore_result=True,
            beat_schedule={
                "task-every-10-seconds": {
                    "task": "app.scrapers.scraper_manager.run_all_scraper_tasks",
                    'schedule': crontab(minute='*'),
                }
            },
        ),
    )

    celery_init_app(app)

    db.init_app(app)
    mongo.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.session_protection = 'strong'
    oauth.init_app(app)
    
    # Remember to import these for oauth login
    from .oauth import github, google, facebook

    # Admin
    admin.init_app(app)
    
    # Cache
    cache.init_app(app)

    from app.models import User, Article
    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(Article, db.session))

    login_manager.login_view = 'login'

    from app.routes import main
    app.register_blueprint(main)

    return app
