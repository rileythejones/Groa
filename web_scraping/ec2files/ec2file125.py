from scraper import * 
s = Scraper(start=222750, end=224531, max_iter=30, scraper_instance=125) 
ids = s.get_ids() 
s.scrape_letterboxd(ids)