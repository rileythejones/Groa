from scraper import * 
s = Scraper(start=212058, end=213839, max_iter=30, scraper_instance=119) 
ids = s.get_ids() 
s.scrape_letterboxd(ids)