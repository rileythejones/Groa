from scraper import * 
s = Scraper(start=174636, end=176417, max_iter=30, scraper_instance=98) 
ids = s.get_ids() 
s.scrape_letterboxd(ids)