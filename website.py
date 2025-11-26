from bs4 import BeautifulSoup
import requests

# Standard headers to fetch a website
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}
class Website:
    """
    A utility class to scrape website contents and links.
    """
    def __init__(self, url, contents_limit=None):
        self.url = url
        try:
            response = requests.get(self.url, headers=headers)
            soup = BeautifulSoup(response.content, "html.parser")
            self.title = soup.title.string if soup.title else "No title found"
            self.text = self.extract_text(soup, limit=contents_limit)
            self.links = self.extract_links(soup)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching the URL {url}: {e}")
            self.title = None
            self.text = None
            self.links = []
            self.url = None
        

    def extract_text(self, soup, limit=None):
        """
        Return the title and contents of the website at the given url;
        truncate to limit characters if specified
        """
        if soup.body:
            for body in soup.body(["script", "style", "img", "input"]):
                body.decompose()
            text = soup.body.get_text(separator="\n", strip=True)
            return text[:limit] if limit else text
        return ""
        
    def extract_links(self, soup):
        links = [link.get("href") for link in soup.find_all("a")]
        return [link for link in links if link]
    
    def get_contents(self):
        """
        Combine title and text content.
        """
        if not self.title and not self.text:
            return ""
        if self.title:
            return f"Webpage Title:\n{self.title}\nWebpage Contents:\n{self.text}\n\n"
        return f"Webpage Contents:\n{self.text}\n\n"


