from scraper import * 
s = Scraper(start=251262, end=253043, max_iter=30, scraper_instance=141) 
ids = s.get_ids() 
s.scrape_letterboxd(ids)