from scraper import * 
s = Scraper(start=5346, end=7127, max_iter=30, scraper_instance=3) 
ids = s.get_ids() 
s.scrape_letterboxd(ids)