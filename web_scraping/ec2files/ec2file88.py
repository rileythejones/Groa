from scraper import * 
s = Scraper(start=156816, end=158597, max_iter=30, scraper_instance=88) 
ids = s.get_ids() 
s.scrape_letterboxd(ids)