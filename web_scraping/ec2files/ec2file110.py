from scraper import * 
s = Scraper(start=196020, end=197801, max_iter=30, scraper_instance=110) 
ids = s.get_ids() 
s.scrape_letterboxd(ids)