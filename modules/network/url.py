import re
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

from utils import log_colorize, colorize
from utils.abc import BaseModule
from utils.consts import SCAN_BANNER


class UrlScanner(BaseModule, name="url-scanner"):
    def __init__(self) -> None:
        self.all_links: set[str] = set()

    @staticmethod
    def is_valid_extension(url: str) -> bool:
        return re.search(r'\.(html|xhtml|php|js|css)$', url) or not re.search(r'\.\w+$', url)

    def extract_links(self, tag, attribute: str, base_url: str, domain: str) -> list[str]:
        links = []
        attr_value = tag.get(attribute)
        if attr_value:
            full_url = urljoin(base_url, attr_value)
            if full_url not in self.all_links and domain in full_url and self.is_valid_extension(full_url):
                links.append(full_url)
                self.all_links.add(full_url)
        return links

    def find_secret_urls(self, website_url: str, domain: str) -> None:
        try:
            response = requests.get(website_url)
            if response.status_code != 200:
                return

            soup = BeautifulSoup(response.content, 'html.parser')
            temp_links = []

            # Collect links from common attributes
            for tag in soup.find_all(['a', 'link', 'script', 'img', 'iframe', 'button', 'form']):
                for attr in ['href', 'src', 'action']:
                    temp_links.extend(self.extract_links(tag, attr, website_url, domain))

            # Collect inline JavaScript links
            for script in soup.find_all('script'):
                if script.string:
                    urls_in_script = re.findall(r'(https?://\S+)', script.string)
                    for url in urls_in_script:
                        if url not in self.all_links and domain in url and self.is_valid_extension(url):
                            temp_links.append(url)
                            self.all_links.add(url)

            for link in temp_links:
                print(f"{log_colorize('URL :', color=0x5386E5, prefix='+')} {link}")

        except requests.RequestException as e:
            print(log_colorize(f"RequestError : {e}", color=0x9487F4, prefix="@"))

    def find_all_secret_urls(self, website_url: str, domain: str) -> None:
        self.find_secret_urls(website_url, domain)
        visited_links = set()

        while True:
            new_links = [link for link in self.all_links if link not in visited_links]
            if not new_links:
                break

            for link in new_links:
                try:
                    self.find_secret_urls(link, domain)
                    visited_links.add(link)
                except Exception as e:
                    print(log_colorize(f"Error : {type(e).__name__} - {e}", color=0x9487F4, prefix="@"))

    def run(self) -> None:
        self.all_links.clear()

        self.print_banner(SCAN_BANNER)
        print(log_colorize("Input network URL", color=0x5386E5, prefix="<"), end="")
        website_url = input().strip()

        if not website_url.startswith(("https://", "http://")):  # noqa
            website_url = "https://" + website_url
        domain = re.sub(r'^https?://', '', website_url).split('/')[0]

        print(colorize("\n>          Only Url (#1)", color=0x5386E5))
        print(colorize(">          All Website (#2)\n", color=0x5386E5))
        print(log_colorize("Choice", color=0x5386E5, prefix="<"), end="")
        choice = input().strip()

        match choice:
            case "1":
                self.find_secret_urls(website_url, domain)
            case "2":
                self.find_all_secret_urls(website_url, domain)


def load() -> BaseModule:
    return UrlScanner()


if __name__ == "__main__":
    with load() as module:
        module.run()
