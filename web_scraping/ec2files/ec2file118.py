from scraper import * 
s = Scraper(start=210276, end=212057, max_iter=30, scraper_instance=118) 
ids = s.get_ids() 
s.scrape_letterboxd(ids)