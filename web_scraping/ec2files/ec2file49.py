from scraper import * 
s = Scraper(start=87318, end=89099, max_iter=30, scraper_instance=49) 
ids = s.get_ids() 
s.scrape_letterboxd(ids)