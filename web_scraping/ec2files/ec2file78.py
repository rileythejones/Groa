from scraper import * 
s = Scraper(start=138996, end=140777, max_iter=30, scraper_instance=78) 
ids = s.get_ids() 
s.scrape_letterboxd(ids)