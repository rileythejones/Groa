from scraper import * 
s = Scraper(start=253044, end=254825, max_iter=30, scraper_instance=142) 
ids = s.get_ids() 
s.scrape_letterboxd(ids)