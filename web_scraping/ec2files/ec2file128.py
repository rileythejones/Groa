from scraper import * 
s = Scraper(start=228096, end=229877, max_iter=30, scraper_instance=128) 
ids = s.get_ids() 
s.scrape_letterboxd(ids)