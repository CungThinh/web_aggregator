import requests
from bs4 import BeautifulSoup

from .base_scraper import BaseScraper


class DevToScraper(BaseScraper):
    def scrape(self):
        url = "https://dev.to"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        for article in soup.find_all('div', class_='crayons-story__body'):
            title_tag = article.find('h2', class_='crayons-story__title')
            if title_tag:
                title = title_tag.get_text(strip=True)
                link = url + title_tag.find('a')['href']

                description_tag = article.find('div', class_='crayons-story__tags')
                description = description_tag.get_text(strip=True) if description_tag else "No description"

                # Finding author
                author_tag = article.find('a', class_='crayons-story__secondary fw-medium m:hidden')
                author = author_tag.get_text(strip=True) if author_tag else "Unknown"

                # Finding image
                image_tag = article.find('img', class_='crayons-article__cover__image__feed')
                image = image_tag['src'] if image_tag else "No image"

                # Finding reading time
                reading_time_tag = article.find('small', class_='crayons-story__tertiary')
                reading_time = reading_time_tag.get_text(strip=True) if reading_time_tag else "Unknown reading time"

                self.articles.append({
                    'title': title,
                    'url': link,
                    'description': description,
                    'author': author,
                    'image': image,
                    'reading_time': reading_time,
                    'category': 'programming'
                })
