from scraper import * 
s = Scraper(start=178200, end=179981, max_iter=30, scraper_instance=100) 
ids = s.get_ids() 
s.scrape_letterboxd(ids)