from scraper import * 
s = Scraper(start=33858, end=35639, max_iter=30, scraper_instance=19) 
ids = s.get_ids() 
s.scrape_letterboxd(ids)