from scraper import * 
s = Scraper(start=57024, end=58805, max_iter=30, scraper_instance=32) 
ids = s.get_ids() 
s.scrape_letterboxd(ids)