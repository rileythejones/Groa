from scraper import * 
s = Scraper(start=231660, end=233441, max_iter=30, scraper_instance=130) 
ids = s.get_ids() 
s.scrape_letterboxd(ids)