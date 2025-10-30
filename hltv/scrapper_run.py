from scrapper_engine import HLTVScraper
from dotenv import load_dotenv
import os
from logger import Logger


load_dotenv()


# filter: get only the matches from 2024 to 2025 and that contain at least one hltv top 20 team (stars=1)
hltv_filter = "&startDate=2024-01-01&endDate=2025-10-23&stars=1"

scrap = HLTVScraper(Logger(), os.getenv('FILEPATH'), hltv_filter=hltv_filter)
scrap.scrape_all_matches()
