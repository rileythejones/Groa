from scraper import * 
s = Scraper(start=165726, end=167507, max_iter=30, scraper_instance=93) 
ids = s.get_ids() 
s.scrape_letterboxd(ids)