from celery import shared_task

from .scrapers.scraper_manager import scraper_registry, run_scraper


@shared_task
def run_all_scraper_tasks():
    for scraper_name in scraper_registry.keys():
        run_scraper(scraper_name)
    print("Done")
