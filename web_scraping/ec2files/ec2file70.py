from scraper import * 
s = Scraper(start=124740, end=126521, max_iter=30, scraper_instance=70) 
ids = s.get_ids() 
s.scrape_letterboxd(ids)