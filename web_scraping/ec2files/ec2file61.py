from scraper import * 
s = Scraper(start=108702, end=110483, max_iter=30, scraper_instance=61) 
ids = s.get_ids() 
s.scrape_letterboxd(ids)