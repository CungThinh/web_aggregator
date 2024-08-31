from app import create_app
from config import DevConfig

flask_app = create_app(DevConfig)
celery_app = flask_app.extensions["celery"]
