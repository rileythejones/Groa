from scraper import * 
s = Scraper(start=169290, end=171071, max_iter=30, scraper_instance=95) 
ids = s.get_ids() 
s.scrape_letterboxd(ids)