from scraper import * 
s = Scraper(start=81972, end=83753, max_iter=30, scraper_instance=46) 
ids = s.get_ids() 
s.scrape_letterboxd(ids)