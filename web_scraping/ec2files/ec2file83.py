from scraper import * 
s = Scraper(start=147906, end=149687, max_iter=30, scraper_instance=83) 
ids = s.get_ids() 
s.scrape_letterboxd(ids)