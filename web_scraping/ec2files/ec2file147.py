from scraper import * 
s = Scraper(start=261954, end=263735, max_iter=30, scraper_instance=147) 
ids = s.get_ids() 
s.scrape_letterboxd(ids)