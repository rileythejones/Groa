from scraper import * 
s = Scraper(start=73062, end=74843, max_iter=30, scraper_instance=41) 
ids = s.get_ids() 
s.scrape_letterboxd(ids)