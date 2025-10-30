import os
import pandas as pd
import undetected_chromedriver as uc
from selenium.common.exceptions import InvalidSessionIdException
from bs4 import BeautifulSoup
import time
import re
from glob import glob
import socket
import urllib.error
from logger import Logger


class HLTVScraper:
    def __init__(self, logger: Logger, filepath: str, hltv_filter: str = None):
        options = uc.ChromeOptions()
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--window-position=-32000,-32000")  # hide window from screen; couldn't do headless, using this instead so one can use the computer screen
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-software-rasterizer")
        options.add_argument('--disable-blink-features=AutomationControlled')

        self.driver = uc.Chrome(options=options)
        self.delay = 2

        self.logger = logger
        self.logger.log("Opening HLTV.org...")
        self.driver.get("https://www.hltv.org")
        time.sleep(self.delay)

        self.filepath = filepath
        self.filter = hltv_filter

    def _get_match_links(self, offset=0):
        url = f"https://www.hltv.org/results?offset={offset}"
        if self.filter is not None:
            url = url + self.filter

        try:
            self.logger.log(f"Loading results page (offset {offset})...")
            if not self._safe_get(url):
                return []
            time.sleep(15)

            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            if self._check_empty_page(soup):
                return []

            match_ids = []
            all_links = soup.find_all('a', href=True)

            for link in all_links:
                href = link['href']
                if '/matches/' in href and re.search(r'/matches/(\d+)/', href):
                    match_id = re.search(r'/matches/(\d+)/', href).group(1)
                    if match_id not in match_ids:
                        match_ids.append(match_id)

            self.logger.log(f"Found {len(match_ids)} match links")
            time.sleep(self.delay)

            return match_ids

        except Exception as e:
            self.logger.log(f"Error getting match links: {e}")
            return []

    @staticmethod
    def _check_empty_page(soup: BeautifulSoup) -> bool:
        empty = soup.find('div', string='No results with the chosen filters')
        return False if empty is None else True

    def _scrape_match_page(self, match_id):
        try:
            self.logger.log('Loading match page...')
            url = f"https://www.hltv.org/matches/{match_id}/x"
            if not self._safe_get(url):
                return False
            time.sleep(5)

            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            stat_link = soup.find('a', href=True, string='Detailed stats')

            stat_url = f'https://www.hltv.org/{stat_link["href"]}'
            if not self._safe_get(stat_url):
                return False
            time.sleep(self.delay)

            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            tables = soup.find_all('table')

            dfs = []
            for idx, table in enumerate(tables):
                if idx not in [0, 3]:
                    continue  # get only the stats for the whole match

                # convert stats table to pandas dataframe
                headers = []
                for th in table.find_all("th"):
                    headers.append(th.get_text(strip=True))

                data = []
                for row in table.find_all("tr"):
                    row_data = [cell.get_text(strip=True) for cell in row.find_all("td")]
                    if row_data:
                        data.append(row_data)

                if headers:
                    df = pd.DataFrame(data, columns=headers)
                else:
                    df = pd.DataFrame(data)

                team_name = df.columns[0]
                df.rename(columns={team_name: 'players'}, inplace=True)
                df['team'] = team_name

                dfs.append(df)

            filename = os.path.join(self.filepath, fr'match_{match_id}.csv')
            pd.concat(dfs).to_csv(filename, index=False)
            self.logger.log(f'File {filename} saved!')
            return True

        except Exception as e:
            if "invalid session id" in str(e).lower():
                self.logger.log(f'Error scrapping match page. Trying to reconnect to chrome...')
                self._restart_chrome()
            else:
                self.logger.log(f'Error scrapping match page: {str(e)}')

            return False

    def scrape_all_matches(self):
        files = glob(os.path.join(self.filepath, '*.csv'))

        try:
            offset = 0
            consecutive_failures = 0

            while consecutive_failures < 2:
                self.logger.log(f"\n{'=' * 60}")
                self.logger.log(f"Processing results page (offset {offset})")
                self.logger.log(f"Progress: {len(files)} matches")
                self.logger.log(f"{'=' * 60}\n")

                match_ids = self._get_match_links(offset)

                if not match_ids:
                    consecutive_failures += 1
                    self.logger.log(f"No matches found (failure #{consecutive_failures})")

                    offset += 100
                    continue

                consecutive_failures = 0  # reset on success

                for match_id in match_ids:
                    # skip if already scraped
                    if any(match_id in m for m in files):
                        self.logger.log(f"({len(files) + 1}) Skipping {match_id} (already scraped)")
                        continue

                    self.logger.log(f"\n({len(files) + 1}) Scraping match {match_id}")

                    # get match page data
                    match_data = self._scrape_match_page(match_id)

                    if match_data:
                        filename = os.path.join(self.filepath, fr'match_{match_id}.csv')
                        files.append(filename)

                offset += 100  # move to next page

        except KeyboardInterrupt:
            self.logger.log(f"Interrupted! {len(files)} matches saved...")

        except Exception as e:
            self.logger.log(f"Unexpected error: {e}")
            self.logger.log(f"Saved {len(files)} matches before error")

        finally:
            self.logger.log("Closing browser...")
            self._safe_close()

    def _safe_get(self, url, max_retries=3):
        for attempt in range(max_retries):
            try:
                self.driver.get(url)
                return True
            except (socket.gaierror, urllib.error.URLError) as e:
                self.logger.log(f"Network error: {e} (attempt {attempt + 1}/{max_retries})")
                time.sleep(5 * (attempt + 1))
            except Exception as e:
                if "invalid session id" in str(e).lower():
                    self.logger.log("Session dead, restarting Chrome...")
                    self._restart_chrome()
                else:
                    self.logger.log(f"Other error while loading {url}: {e}")
                time.sleep(5)
        self.logger.log(f"Failed to load {url} after {max_retries} retries")
        return False

    def _safe_close(self):
        try:
            self.driver.quit()
        except InvalidSessionIdException:
            self.logger.log("Driver already quit (ignored)")
        except Exception as e:
            self.logger.log(f"Error quitting driver: {e}")

    def _restart_chrome(self, wait_time: int = 60):
        self.logger.log("\nRestarting Chrome driver...")
        self._safe_close()
        time.sleep(wait_time)  # quit driver and wait before restarting (trying to avoid connection timeout)

        options = uc.ChromeOptions()
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--window-position=-32000,-32000")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-software-rasterizer")
        options.add_argument('--disable-blink-features=AutomationControlled')

        self.driver = uc.Chrome(options=options)

        self.logger.log("Reopening HLTV.org...")
        self.driver.get("https://www.hltv.org")
        time.sleep(self.delay)
