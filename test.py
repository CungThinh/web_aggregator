from app import create_app
from config import DevConfig
from app.models import Article
from flask import url_for
from app import db

app = create_app(DevConfig)
with app.app_context():
    articles = Article.query.filter_by(category="programming").all()
    default_image_url = url_for('static', filename='images/devto_img.png')
    print(default_image_url)
    # for article in articles:
    #     article.image = default_image_url
    #     db.session.save(article)
    #     db.session.commit()
    
