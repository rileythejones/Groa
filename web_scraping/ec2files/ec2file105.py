from scraper import * 
s = Scraper(start=187110, end=188891, max_iter=30, scraper_instance=105) 
ids = s.get_ids() 
s.scrape_letterboxd(ids)