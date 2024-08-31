import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from .base_scraper import BaseScraper


class SpiderumScraper(BaseScraper):
    def scrape(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        driver = webdriver.Chrome(options=options)

        url = "https://spiderum.com/danh-muc/phat-trien-ban-than?sort=hot&page_idx=1"
        driver.get(url)
        body = driver.find_element(By.TAG_NAME, 'body')

        for _ in range(10):
            body.send_keys(Keys.PAGE_DOWN)
            time.sleep(1)

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        main_container = soup.find('div', class_='card-gallery is-medium has-separator feed-wrapper ng-star-inserted')

        if main_container:
            self.articles.extend([
                {
                    'title': article.find('h1', class_='title').get_text(strip=True) if article.find('h1',
                                                                                                     class_='title') else "No title",
                    'url': "https://spiderum.com" + article.find('a', class_='thumbnail')['href'] if article.find('a',
                                                                                                                  class_='thumbnail') else "No link",
                    'description': "",

                    'author': article.find('div', class_='author').get_text(strip=True) if article.find('div',
                                                                                                        class_='author') else "Unknown",
                    'image': article.find('img')['src'] if article.find('img') else "No image",

                    'reading_time': article.find('div', class_='created-at ng-star-inserted').get_text(
                        strip=True) if article.find('div', class_='created-at ng-star-inserted') else "No text",
                    'category': 'self-improvement',
                }
                for article in main_container.find_all('spiderum-card')
            ])

        # Use extend for better performance

        driver.quit()
