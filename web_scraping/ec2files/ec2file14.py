from scraper import * 
s = Scraper(start=24948, end=26729, max_iter=30, scraper_instance=14) 
ids = s.get_ids() 
s.scrape_letterboxd(ids)