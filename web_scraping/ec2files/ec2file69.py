from scraper import * 
s = Scraper(start=122958, end=124739, max_iter=30, scraper_instance=69) 
ids = s.get_ids() 
s.scrape_letterboxd(ids)