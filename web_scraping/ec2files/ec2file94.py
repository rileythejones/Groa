from scraper import * 
s = Scraper(start=167508, end=169289, max_iter=30, scraper_instance=94) 
ids = s.get_ids() 
s.scrape_letterboxd(ids)