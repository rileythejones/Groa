from scraper import * 
s = Scraper(start=188892, end=190673, max_iter=30, scraper_instance=106) 
ids = s.get_ids() 
s.scrape_letterboxd(ids)