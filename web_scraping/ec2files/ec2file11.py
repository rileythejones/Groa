from scraper import * 
s = Scraper(start=19602, end=21383, max_iter=30, scraper_instance=11) 
ids = s.get_ids() 
s.scrape_letterboxd(ids)