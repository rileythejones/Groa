from scraper import * 
s = Scraper(start=80190, end=81971, max_iter=30, scraper_instance=45) 
ids = s.get_ids() 
s.scrape_letterboxd(ids)