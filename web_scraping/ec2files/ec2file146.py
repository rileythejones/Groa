from scraper import * 
s = Scraper(start=260172, end=261953, max_iter=30, scraper_instance=146) 
ids = s.get_ids() 
s.scrape_letterboxd(ids)