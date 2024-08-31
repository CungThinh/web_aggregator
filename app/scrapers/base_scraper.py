from app import db
from ..models import Article


class BaseScraper:
    def __init__(self):
        self.articles = []

    def scrape(self):
        raise NotImplementedError("Subclass need to implement this")

    def save_to_database(self) -> None:
        existing_urls = {article.url for article in
                         Article.query.filter(Article.url.in_([data['url'] for data in self.articles])).all()}
        new_articles = []

        for data in self.articles:
            if data['url'] not in existing_urls:
                new_articles.append(Article(
                    author=data['author'],
                    title=data['title'],
                    url=data['url'],
                    description=data['description'],
                    image=data['image'],
                    reading_time=data['reading_time'],
                    category=data['category'],
                ))
        if new_articles:
            db.session.bulk_save_objects(new_articles)
            db.session.commit()
