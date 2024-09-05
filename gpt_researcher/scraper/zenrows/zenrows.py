import os
from bs4 import BeautifulSoup
from zenrows import ZenRowsClient

PREMIUM_PROXY_DOMAINS = ["reddit.com", "twitter.com", "linkedin.com", "instagram.com"]


class ZenRowsScraper:

    def __init__(self, link, session=None):
        self.client = ZenRowsClient(apikey=self.get_api_key(), concurrency=20)
        self.link = link
        self.session = session

    def get_api_key(self):
        """
        Gets the Scraping Bee API key
        Returns:

        """
        api_key = ""
        try:
            api_key = os.environ["ZEN_ROWS_API_KEY"]
        except KeyError:
            raise Exception(
                "Scraping Bee API key not found. Please set the ZEN_ROWS_API_KEY environment variable."
            )
        return api_key

    def scrape(self):
        """
        Send requests to ScraperAPI and parse data from the HTML response.
        """
        print("zenrows - request - url: " + self.link)
        try:
            response = self.client.get(
                self.link,
                params={
                    "js_render": "true",
                    "premium_proxy": (
                        True
                        if any(domain in self.link for domain in PREMIUM_PROXY_DOMAINS)
                        else False
                    ),
                },
            )

            print("zenrows - response - status_code: " + str(response.status_code))

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
