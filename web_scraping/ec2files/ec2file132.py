from scraper import * 
s = Scraper(start=235224, end=237005, max_iter=30, scraper_instance=132) 
ids = s.get_ids() 
s.scrape_letterboxd(ids)