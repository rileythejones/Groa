from scraper import * 
s = Scraper(start=51359, end=53129, max_iter=30, scraper_instance=29) 
ids = s.get_ids() 
s.scrape_letterboxd(ids)