from scraper import * 
s = Scraper(start=229878, end=231659, max_iter=30, scraper_instance=129) 
ids = s.get_ids() 
s.scrape_letterboxd(ids)