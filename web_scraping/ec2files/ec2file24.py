from scraper import * 
s = Scraper(start=42768, end=44549, max_iter=30, scraper_instance=24) 
ids = s.get_ids() 
s.scrape_letterboxd(ids)