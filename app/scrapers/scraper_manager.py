from celery import shared_task

from app.scrapers.devto_scraper import DevToScraper
from app.scrapers.spiderum_scraper import SpiderumScraper
import logging

logger = logging.getLogger(__name__)

scraper_registry = {
    'devto': DevToScraper,
    'spiderum': SpiderumScraper
}


def run_scraper(scraper_name):
    scraper_class = scraper_registry.get(scraper_name)
    if scraper_class:
        scraper = scraper_class()
        scraper.scrape()
        scraper.save_to_database()
    else:
        raise ValueError(f"No scraper found")


@shared_task
def run_all_scraper_tasks():
    for scraper_name in scraper_registry.keys():
        run_scraper(scraper_name)
    logger.info("Hoan Thanh")
