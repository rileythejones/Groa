from scraper import * 
s = Scraper(start=172854, end=174635, max_iter=30, scraper_instance=97) 
ids = s.get_ids() 
s.scrape_letterboxd(ids)