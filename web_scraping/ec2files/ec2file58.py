from scraper import * 
s = Scraper(start=103356, end=105137, max_iter=30, scraper_instance=58) 
ids = s.get_ids() 
s.scrape_letterboxd(ids)