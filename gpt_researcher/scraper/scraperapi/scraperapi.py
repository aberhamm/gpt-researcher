import requests
from bs4 import BeautifulSoup
import concurrent.futures
from urllib.parse import urlencode
import os


class ScraperAPI:
    def __init__(self, num_retries=5):
        self.api_key = self.get_api_key()
        self.num_retries = num_retries

    def get_api_key(self):
        """
        Gets the Scraperapi API key
        Returns:

        """
        api_key = ""
        try:
            api_key = os.environ["SCRAPERAPI_API_KEY"]
        except KeyError:
            raise Exception(
                "Scraperapi API key not found. Please set the SCRAPERAPI_API_KEY environment variable."
            )
        return api_key

    def scrape_url(self, url):
        """
        Send requests to ScraperAPI and parse data from the HTML response.
        """
        params = {"api_key": self.api_key, "url": url}

        for _ in range(self.num_retries):
            try:
                response = requests.get(
                    "http://api.scraperapi.com/", params=urlencode(params)
                )
                if response.status_code in [200, 404]:
                    break
            except requests.exceptions.ConnectionError:
                response = None

        if response and response.status_code == 200:
            html_response = response.text
            return html_response

        return ""
