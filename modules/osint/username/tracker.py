import json
import re
import threading

import requests
from bs4 import BeautifulSoup

from utils import log_colorize
from utils.abc import BaseModule
from utils.consts import OSINT_BANNER


class UsernameLookup(BaseModule, name="lookup"):
    def __init__(self) -> None:
        self.founded: dict[str, str] = {}

    @classmethod
    def site_exception(cls, username: str, site: str, page_content: str) -> str:
        match site:
            case "Paypal":
                page_content = (
                    page_content.
                    replace(f'slug_name={username}', '').
                    replace(f'"slug":"{username}"', '').
                    replace(f'2F{username}&amp', '')
                )
            case "TikTok":
                page_content = page_content.replace(f'\\u002f@{username}"', '')

        return page_content

    @classmethod
    def maybe_not_found(cls, text: str) -> bool:
        soup = BeautifulSoup(text, "html.parser")
        page_title = soup.title.string.strip() if soup.title else ""

        for error_indicator in [
            "This profile could not be found",
            "Sorry, this user was not found",
            "Page Not Found",
            "the profile was either removed ",
            "The specified profile could not be found",
            "doesn&apos;t&nbsp;exist",
            "This page doesn't exist",
            "404 Not Found",
            "Sorry, nobody on Reddit goes by that name",
            "The person may have been banned or the username is incorrect.",
            "Some error occured while loading page for you. Please try again",
            "No longer a registered user",
            "No user ID specified or user does not exist!",
            "user does not exist",
            "User not found.",
            "User was not found.",
            "An error was encountered while processing your request",
            "Sorry, the page you were looking for doesn’t exist",
            "Wikipedia does not have a",
            "We could not find the page you were looking for, so we found something to make you laugh to make up for it",
            "Not Found!",
            '"statusMsg":"","needFix"',
            "is still available",
        ]:
            if (
                    error_indicator.lower() in text.lower()
                    or error_indicator.lower() in page_title.lower()
                    or page_title.lower() == "instagram"
                    or page_title.lower() == "patreon logo"
                    or "sign in" in page_title.lower()
            ):
                return True
        return False

    @staticmethod
    def get_sites(file_path: str) -> dict[str, str]:
        try:
            with open(file_path, encoding="UTF-8", mode="r+") as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    def check_site(self, site: str, url_template: str, username: str) -> None:
        url = url_template.replace("{user}", username)
        try:
            response = requests.get(url, timeout=10)
            if (
                    response.status_code == 200
                    and not self.maybe_not_found(response.text)
            ):
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
                    self.founded[site] = url
                    print(log_colorize(f"{site.upper()} : {url}", color=0x6BFF73, prefix="+"))
                return
        except Exception as e:
            print(log_colorize(f"{site.upper()} : {e}", color=0x9487F4, prefix="@"))
        else:
            print(log_colorize(f"{site.upper()} not found", color=0x9487F4, prefix="@"))

    def run(self) -> None:
        self.print_banner(OSINT_BANNER)
        self.founded.clear()

        print(log_colorize("Input username", color=0x5386E5, prefix="<"), end="")
        username = input().lower()

        print(log_colorize("Input sites.json file path", color=0x5386E5, prefix="<"), end="")
        file_path = input().lower()

        sites = self.get_sites(file_path)
        if not sites:
            print(log_colorize("Invalid sites.json file path", color=0x9487F4, prefix=">"))
            return

        threads = []

        for site, url_template in sites.items():
            thread = threading.Thread(target=self.check_site, args=(site, url_template, username))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        print()

        if not self.founded:
            print(log_colorize("No website found", color=0x5386E5, prefix=">"))
        else:
            print(log_colorize("Found on the following websites:", color=0x5386E5, prefix=">"))
            for site, url in self.founded.items():
                print(log_colorize(f"{site.upper()} : {url}", color=0x6BFF73, prefix="+"))

            print(log_colorize(f"Total found: {len(self.founded)}", color=0x5386E5, prefix=">"))


def load() -> BaseModule:
    return UsernameLookup()


if __name__ == "__main__":
    with load() as module:
        module: BaseModule
        module.run()
