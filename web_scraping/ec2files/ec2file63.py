from scraper import * 
s = Scraper(start=112266, end=114047, max_iter=30, scraper_instance=63) 
ids = s.get_ids() 
s.scrape_letterboxd(ids)