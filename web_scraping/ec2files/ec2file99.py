from scraper import * 
s = Scraper(start=176418, end=178199, max_iter=30, scraper_instance=99) 
ids = s.get_ids() 
s.scrape_letterboxd(ids)