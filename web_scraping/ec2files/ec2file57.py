from scraper import * 
s = Scraper(start=101574, end=103355, max_iter=30, scraper_instance=57) 
ids = s.get_ids() 
s.scrape_letterboxd(ids)