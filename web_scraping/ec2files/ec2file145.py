from scraper import * 
s = Scraper(start=258390, end=260171, max_iter=30, scraper_instance=145) 
ids = s.get_ids() 
s.scrape_letterboxd(ids)