from scraper import * 
s = Scraper(start=99792, end=101573, max_iter=30, scraper_instance=56) 
ids = s.get_ids() 
s.scrape_letterboxd(ids)