import json
import re

import requests
from bs4 import BeautifulSoup

from utils import log_colorize
from utils.abc import BaseModule
from utils.consts import OSINT_BANNER


class UsernameLookup(BaseModule, name="lookup"):

    @classmethod
    def site_exception(cls, username: str, site: str, page_content: str) -> str:
        if site == "Paypal":
            page_content = (
                page_content.
                replace(f'slug_name={username}', '').
                replace(f'"slug":"{username}"', '').
                replace(f'2F{username}&amp', '')
            )

        elif site == "TikTok":
            page_content = page_content.replace(f'\\u002f@{username}"', '')

        return page_content

    @staticmethod
    def get_sites(file_path: str) -> dict[str, str]:
        try:
            with open(file_path, encoding="UTF-8", mode="r+") as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    def run(self) -> None:
        self.print_banner(OSINT_BANNER)

        print(log_colorize("Input username", color=0x5386E5, prefix="<"), end="")
        username = input().lower()

        print(log_colorize("Input sites.json file path", color=0x5386E5, prefix="<"), end="")
        file_path = input().lower()

        sites = self.get_sites(file_path)
        if not sites:
            print(log_colorize("Invalid sites.json file path", color=0x9487F4, prefix=">"))
            return

        founded_sites: dict[str, str] = {}
        for site, url_template in sites.items():
            url = url_template.replace("{user}", username)

            try:
                response = requests.get(url, timeout=3)
                if response.status_code == 200:
                    page_content = re.sub(
                        r'<[^>]*>', '',
                        response.text.
                        lower().
                        replace(url, "").
                        replace(f"/{username}", "")
                    )

                    page_content = self.site_exception(username, site, page_content)
                    page_text = BeautifulSoup(response.text, 'html.parser').get_text().lower().replace(url, "")
                    page_title = BeautifulSoup(response.content, 'html.parser').title.string.lower()

                    if (
                            username in page_title
                            or username in page_content
                            or username in page_text
                    ):
                        founded_sites[site] = url
                        print(log_colorize(f"{site.upper()} : {url}", color=0x6BFF73, prefix="+"))

                        continue

                    print(log_colorize(f"{site.upper()} not found", color=0x9487F4, prefix="-"))

            except Exception as e:
                print(log_colorize(f"{site.upper()} : {e}", color=0x9487F4, prefix="@"))

        print()

        if not founded_sites:
            print(log_colorize("No website found", color=0x5386E5, prefix=">"))
        else:
            print(log_colorize("Found on the following websites:", color=0x5386E5, prefix=">"))
            for site, url in founded_sites.items():
                print(log_colorize(f"{site.upper()} : {url}", color=0x6BFF73, prefix="+"))

            print(log_colorize(f"Total founded: {len(founded_sites)}", color=0x5386E5, prefix=">"))

def load() -> BaseModule:
    return UsernameLookup()


if __name__ == "__main__":
    with load() as module:
        module: BaseModule
        module.run()
