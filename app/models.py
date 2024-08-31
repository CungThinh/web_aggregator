from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), unique=True, nullable=True)
    provider = db.Column(db.String(50), nullable=True)  # OAuth provider (e.g., Google)
    provider_user_id = db.Column(db.String(200), nullable=True, unique=True)  # User ID from OAuth provider
    access_token = db.Column(db.String(500), nullable=True)  # OAuth access token

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        return f'<User {self.username or self.email}>'


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(50), nullable=True)
    title = db.Column(db.String(200), nullable=True)
    url = db.Column(db.String(200), nullable=True)
    description = db.Column(db.String(200), nullable=True)
    image = db.Column(db.String(200), nullable=True)
    reading_time = db.Column(db.String(50), nullable=True)
    category = db.Column(db.String(50), nullable=False)
