from scraper import * 
s = Scraper(start=89100, end=90881, max_iter=30, scraper_instance=50) 
ids = s.get_ids() 
s.scrape_letterboxd(ids)