from scraper import * 
s = Scraper(start=3564, end=5345, max_iter=30, scraper_instance=2) 
ids = s.get_ids() 
s.scrape_letterboxd(ids)