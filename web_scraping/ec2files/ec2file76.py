from scraper import * 
s = Scraper(start=135432, end=137213, max_iter=30, scraper_instance=76) 
ids = s.get_ids() 
s.scrape_letterboxd(ids)