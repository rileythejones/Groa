from scraper import * 
s = Scraper(start=76626, end=78407, max_iter=30, scraper_instance=43) 
ids = s.get_ids() 
s.scrape_letterboxd(ids)