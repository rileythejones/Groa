from scraper import * 
s = Scraper(start=23166, end=24947, max_iter=30, scraper_instance=13) 
ids = s.get_ids() 
s.scrape_letterboxd(ids)