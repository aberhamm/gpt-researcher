import os
from bs4 import BeautifulSoup
from scrapingbee import ScrapingBeeClient

PREMIUM_PROXY_DOMAINS = ["reddit.com", "twitter.com", "linkedin.com", "instagram.com"]


class ScrapingBeeScraper:

    def __init__(self, link, session=None):
        self.client = ScrapingBeeClient(api_key=self.get_api_key())
        self.link = link
        self.session = session

    def get_api_key(self):
        """
        Gets the Scraping Bee API key
        Returns:

        """
        api_key = ""
        try:
            api_key = os.environ["SCRAPING_BEE_API_KEY"]
        except KeyError:
            raise Exception(
                "Scraping Bee API key not found. Please set the SCRAPING_BEE_API_KEY environment variable."
            )
        return api_key

    def scrape(self):
        """
        Send requests to ScraperAPI and parse data from the HTML response.
        """
        print("scraping bee - request - url: " + self.link)
        try:
            response = self.client.get(
                url=self.link,
                params={
                    # Block ads on the page you want to scrape
                    "block_ads": True,
                    # Block images and CSS on the page you want to scrape
                    "block_resources": True,
                    # Use premium proxies to bypass difficult to scrape websites (10-25 credits/request)
                    "premium_proxy": (
                        True
                        if any(domain in self.link for domain in PREMIUM_PROXY_DOMAINS)
                        else False
                    ),
                    # Execute JavaScript code with a Headless Browser (5 credits/request)
                    "render_js": True,
                },
                retries=2,
            )

            print("scraping bee - response - status_code: " + str(response.status_code))

            soup = BeautifulSoup(
                response.content, "lxml", from_encoding=response.encoding
            )

            for script_or_style in soup(["script", "style"]):
                script_or_style.extract()

            raw_content = self.parse_page(soup)
            lines = (line.strip() for line in raw_content.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text_content = "\n".join(chunk for chunk in chunks if chunk)
            return text_content
        except Exception as e:
            print("Error: " + str(e))
            return ""

    def parse_page(self, soup):
        """Get the text from the soup

        Args:
            soup (BeautifulSoup): The soup to get the text from

        Returns:
            str: The text from the soup
        """
        text = ""
        tags = ["p", "h1", "h2", "h3", "h4", "h5"]
        for element in soup.find_all(tags):  # Find all the <p> elements
            text += element.text + "\n"
        return text

    def parse_reddit_page(self, soup):
        """Get the text from the soup

        Args:
            soup (BeautifulSoup): The soup to get the text from

        Returns:
            str: The text from the soup
        """
        comment_array = []
        cssClasses = ["usertext-body"]
        for element in soup.find_all(class_=cssClasses):
            if element.text and element.text.strip() != "":
                comment_array.append(element.text)

        text_content = ""
        for index, comment in enumerate(comment_array):
            text_content += f"Comment {index + 1}:\n{comment}\n"

        return text_content
