import json
from dataclasses import dataclass
from typing import Optional

from bs4 import BeautifulSoup
from fake_useragent import FakeUserAgent
from requests import Session

from utils import log_colorize
from utils.abc import BaseModule
from utils.consts import OSINT_BANNER


@dataclass
class Response:
    status_code: int
    message: Optional[str]
    error: Optional[str]


class EmailTracker(BaseModule, name="tracker"):
    def __init__(self) -> None:
        self.session: Session = Session()
        self._user_agent: FakeUserAgent = FakeUserAgent()

    def try_instagram(self, email: str) -> Response:
        headers: dict = {
            'User-Agent': self._user_agent.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Origin': 'https://www.instagram.com',
            'Connection': 'keep-alive',
            'Referer': 'https://www.instagram.com/'
        }

        try:
            response = self.session.get(
                "https://www.instagram.com/accounts/emailsignup/",
                headers=headers
            )
            if response.status_code == 200:
                if 'csrftoken' in self.session.cookies:
                    token = self.session.cookies['csrftoken']
                else:
                    return Response(
                        status_code=response.status_code,
                        message=None,
                        error="Instagram signup token cannot be found in cookies."
                    )
            else:
                return Response(
                    status_code=response.status_code,
                    message=None,
                    error="Unable to process a status other than 200."
                )

            headers["x-csrftoken"] = token
            headers["Referer"] = "https://www.instagram.com/accounts/emailsignup/"

            response = self.session.post(
                url="https://www.instagram.com/api/v1/web/accounts/web_create_ajax/attempt/",
                headers=headers,
                data={
                    "osint": email
                }
            )
            if response.status_code == 200:
                if (
                        ("Another account is using the same osint." in response.text)
                        or ("email_is_taken" in response.text)
                ):
                    return Response(
                        status_code=response.status_code,
                        message="Account registered.",
                        error=None
                    )
                else:
                    return Response(
                        status_code=response.status_code,
                        message=None,
                        error="Account not registered."
                    )
            else:
                return Response(
                    status_code=response.status_code,
                    message=None,
                    error="Unknown status code."
                )
        except Exception as e:
            return Response(
                status_code=400,
                message=None,
                error=f"We get an exception while requesting: {e}."
            )

    def try_x(self, email: str) -> Response:
        try:
            response = self.session.get(
                url="https://api.x.com/i/users/email_available.json",
                params={
                    "osint": email
                }
            )
            if response.status_code == 200:
                if response.json().get("taken"):
                    return Response(
                        status_code=response.status_code,
                        message="Account registered.",
                        error=None
                    )
                else:
                    return Response(
                        status_code=response.status_code,
                        message=None,
                        error="Account not registered."
                    )
            else:
                return Response(
                    status_code=response.status_code,
                    message=None,
                    error="Unknown status code."
                )
        except Exception as e:
            return Response(
                status_code=400,
                message=None,
                error=f"We get an exception while requesting: {e}."
            )

    def try_pinterest(self, email: str) -> Response:
        try:
            response = self.session.get(
                "https://www.pinterest.com/_ngjs/resource/EmailExistsResource/get/",
                params={
                    "source_url": "/",
                    "data": json.dumps({"options": {"osint": email}, "context": {}})
                }
            )

            if response.status_code == 200:
                data = response.json()
                if (data["resource_response"]["message"] == "ok") or (data["resource_response"].get("data")):
                    return Response(
                        status_code=response.status_code,
                        message="Account registered.",
                        error=None
                    )

                return Response(
                    status_code=response.status_code,
                    message=None,
                    error="Account not registered."
                )
            else:
                return Response(
                    status_code=response.status_code,
                    message=None,
                    error="Unknown status code."
                )
        except Exception as e:
            return Response(
                status_code=400,
                message=None,
                error=f"We get an exception while requesting: {e}."
            )

    def try_imgur(self, email: str) -> Response:
        headers = {
            'User-Agent': self._user_agent.random,
            'Accept': '*/*',
            'Accept-Language': 'en,en-US;q=0.5',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://imgur.com',
            'DNT': '1',
            'Connection': 'keep-alive',
            'TE': 'Trailers',
            "X-Requested-With": "XMLHttpRequest"
        }

        try:
            response = self.session.post(
                'https://imgur.com/signin/ajax_email_available',
                headers=headers,
                data={
                    'osint': email
                }
            )

            if response.status_code == 200:
                if (not response.json()["data"]["available"]) or ("Invalid osint domain" not in response.text):
                    return Response(
                        status_code=response.status_code,
                        message="Account registered.",
                        error=None
                    )

                return Response(
                    status_code=response.status_code,
                    message=None,
                    error="Account not registered."
                )
            else:
                return Response(
                    status_code=response.status_code,
                    message=None,
                    error="Unknown status code."
                )
        except Exception as e:
            return Response(
                status_code=400,
                message=None,
                error=f"We get an exception while requesting: {e}."
            )

    def try_patreon(self, email: str) -> Response:
        headers = {
            'User-Agent': self._user_agent.random,
            'Accept': '*/*',
            'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': 'https://www.plurk.com',
            'DNT': '1',
            'Connection': 'keep-alive',
        }

        try:
            response = self.session.post(
                'https://www.plurk.com/Users/isEmailFound',
                headers=headers,
                data={
                    'osint': email
                })
            if response.status_code == 200:
                if "True" in response.text:
                    return Response(
                        status_code=response.status_code,
                        message="Account registered.",
                        error=None
                    )

                return Response(
                    status_code=response.status_code,
                    message=None,
                    error="Account not registered."
                )
            else:
                return Response(
                    status_code=response.status_code,
                    message=None,
                    error="Unknown status code."
                )
        except Exception as e:
            return Response(
                status_code=400,
                message=None,
                error=f"We get an exception while requesting: {e}."
            )

    def try_spotify(self, email: str) -> Response:
        headers = {
            'User-Agent': self._user_agent.random,
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.5',
            'DNT': '1',
            'Connection': 'keep-alive',
        }

        try:
            response = self.session.get(
                'https://spclient.wg.spotify.com/signup/public/v1/account',
                headers=headers,
                params={
                    'validate': '1',
                    'osint': email,
                }
            )
            if response.status_code == 200:
                if response.json()["status"] == 20:
                    return Response(
                        status_code=response.status_code,
                        message="Account registered.",
                        error=None
                    )

                return Response(
                    status_code=response.status_code,
                    message=None,
                    error="Account not registered."
                )
            else:
                return Response(
                    status_code=response.status_code,
                    message=None,
                    error="Unknown status code."
                )
        except Exception as e:
            return Response(
                status_code=400,
                message=None,
                error=f"We get an exception while requesting: {e}."
            )

    def try_firefox(self, email: str) -> Response:
        try:
            response = self.session.post(
                "https://api.accounts.firefox.com/v1/account/status",
                data={
                    "osint": email
                }
            )

            if response.status_code == 200:
                if "true" in response.text:
                    return Response(
                        status_code=response.status_code,
                        message="Account registered.",
                        error=None
                    )

                return Response(
                    status_code=response.status_code,
                    message=None,
                    error="Account not registered."
                )
            else:
                return Response(
                    status_code=response.status_code,
                    message=None,
                    error="Unknown status code."
                )
        except Exception as e:
            return Response(
                status_code=400,
                message=None,
                error=f"We get an exception while requesting: {e}."
            )

    def try_lastpass(self, email: str) -> Response:
        headers = {
            'User-Agent': self._user_agent.random,
            'Accept': '*/*',
            'Accept-Language': 'en,en-US;q=0.5',
            'Referer': 'https://lastpass.com/',
            'X-Requested-With': 'XMLHttpRequest',
            'DNT': '1',
            'Connection': 'keep-alive',
            'TE': 'Trailers',
        }

        try:
            response = self.session.get(
                'https://lastpass.com/create_account.php',
                params={
                    'check': 'avail',
                    'skipcontent': '1',
                    'mistype': '1',
                    'username': email,
                },
                headers=headers
            )

            if response.status_code == 200:
                if "no" in response.text:
                    return Response(
                        status_code=response.status_code,
                        message="Account registered.",
                        error=None
                    )

                return Response(
                    status_code=response.status_code,
                    message=None,
                    error="Account not registered."
                )
            else:
                return Response(
                    status_code=response.status_code,
                    message=None,
                    error="Unknown status code."
                )
        except Exception as e:
            return Response(
                status_code=400,
                message=None,
                error=f"We get an exception while requesting: {e}."
            )

    def try_archive(self, email: str) -> Response:
        headers = {
            'User-Agent': self._user_agent.random,
            'Accept': '*/*',
            'Accept-Language': 'en,en-US;q=0.5',
            'Content-Type': 'multipart/form-data; boundary=---------------------------',
            'Origin': 'https://archive.org',
            'Connection': 'keep-alive',
            'Referer': 'https://archive.org/account/signup',
            'Sec-GPC': '1',
            'TE': 'Trailers',
        }

        try:
            data = '-----------------------------\r\nContent-Disposition: form-data; name="input_name"\r\n\r\nusername\r\n-----------------------------\r\nContent-Disposition: form-data; name="input_value"\r\n\r\n' + email + \
                   '\r\n-----------------------------\r\nContent-Disposition: form-data; name="input_validator"\r\n\r\ntrue\r\n-----------------------------\r\nContent-Disposition: form-data; name="submit_by_js"\r\n\r\ntrue\r\n-------------------------------\r\n'

            response = self.session.post(
                'https://archive.org/account/signup',
                headers=headers,
                data=data
            )
            if response.status_code == 200:
                if "is already taken." in response.text:
                    return Response(
                        status_code=response.status_code,
                        message="Account registered.",
                        error=None
                    )

                return Response(
                    status_code=response.status_code,
                    message=None,
                    error="Account not registered."
                )
            else:
                return Response(
                    status_code=response.status_code,
                    message=None,
                    error="Unknown status code."
                )
        except Exception as e:
            return Response(
                status_code=400,
                message=None,
                error=f"We get an exception while requesting: {e}."
            )

    def try_pornhub(self, email: str) -> Response:
        headers = {
            'User-Agent': self._user_agent.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en,en-US;q=0.5',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        try:
            response = self.session.get("https://www.pornhub.com/signup", headers=headers)
            if response.status_code == 200:
                token = BeautifulSoup(response.content, features="html.parser").find(attrs={"name": "token"})

                if token is None:
                    return Response(
                        status_code=400,
                        message=None,
                        error=f"PornHub token not found"
                    )

                token = token.get("value")
            else:
                return Response(
                    status_code=response.status_code,
                    message=None,
                    error=f"We get an exception while requesting: {response.text}."
                )

            response = self.session.post(
                'https://www.pornhub.com/user/create_account_check',
                headers=headers,
                params={
                    'token': token,
                },
                data={
                    'check_what': 'osint',
                    'osint': email
                }
            )
            if response.status_code == 200:
                if (
                        (response.json()["error_message"] == "Email has been taken.")
                        or "Email has been taken." in response.text
                ):
                    return Response(
                        status_code=response.status_code,
                        message="Account registered.",
                        error=None
                    )

                return Response(
                    status_code=response.status_code,
                    message=None,
                    error="Account not registered."
                )
            else:
                return Response(
                    status_code=response.status_code,
                    message=None,
                    error="Unknown status code."
                )
        except Exception as e:
            return Response(
                status_code=400,
                message=None,
                error=f"We get an exception while requesting: {e}."
            )

    def try_xnxx(self, email: str) -> Response:
        headers = {
            'User-Agent': self._user_agent.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-en',
            'Host': 'www.xnxx.com',
            'Referer': 'https://www.google.com/',
            'Connection': 'keep-alive'
        }
        try:
            response = self.session.get('https://www.xnxx.com', headers=headers)

            if response.status_code == 200:
                if not response:
                    return Response(
                        status_code=response.status_code,
                        message=None,
                        error="Cookie not found."
                    )
            else:
                return Response(
                    status_code=response.status_code,
                    message=None,
                    error="Unknown status code."
                )

            headers['Referer'] = 'https://www.xnxx.com/video-holehe/palenath_fucks_xnxx_with_holehe'
            headers['X-Requested-With'] = 'XMLHttpRequest'

            response = self.session.get(
                f'https://www.xnxx.com/account/checkemail',
                headers=headers,
                cookies=response.cookies,
                params={
                    "osint": email
                }
            )

            if response.status_code == 200:
                data = response.json()
                if (
                        (data['result'] == "false")
                        or (data['code'] == 1)
                        or "This osint is already in use" in data.get("message", "")
                ):
                    return Response(
                        status_code=response.status_code,
                        message="Account registered.",
                        error=None
                    )

                return Response(
                    status_code=response.status_code,
                    message=None,
                    error="Account not registered."
                )
            else:
                return Response(
                    status_code=response.status_code,
                    message=None,
                    error="Unknown status code."
                )
        except Exception as e:
            return Response(
                status_code=400,
                message=None,
                error=f"We get an exception while requesting: {e}."
            )

    def try_xvideo(self, email: str) -> Response:
        headers = {
            'User-Agent': self._user_agent.random,
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'Connection': 'keep-alive',
            'Referer': 'https://www.xvideos.com/',
        }

        try:
            response = self.session.get(
                'https://www.xvideos.com/account/checkemail',
                headers=headers,
                params={
                    'osint': email,
                }
            )

            if response.status_code == 200:
                data = response.json()
                if (
                        (data['result'] == "false")
                        or "This osint is already in use" in data.get("message", "")
                        or (data['code'] == 1)
                ):
                    return Response(
                        status_code=response.status_code,
                        message="Account registered.",
                        error=None
                    )

                return Response(
                    status_code=response.status_code,
                    message=None,
                    error="Account not registered."
                )
            else:
                return Response(
                    status_code=response.status_code,
                    message=None,
                    error="Unknown status code."
                )
        except Exception as e:
            return Response(
                status_code=400,
                message=None,
                error=f"We get an exception while requesting: {e}."
            )

    def run(self) -> None:
        self.print_banner(OSINT_BANNER)
        print(log_colorize("Input email address", color=0x5386E5, prefix="<"), end="")
        email = input()

        for site in [
            "instagram",
            "x",
            "pinterest",
            "imgur",
            "patreon",
            "spotify",
            "firefox",
            "lastpass",
            "archive",
            "pornhub",
            "xnxx",
            "xvideo"
        ]:
            try:
                response = getattr(self, f"try_{site}")(email)
                print(log_colorize(
                    f"{site.upper()} : {response.message or response.error}",
                    color=0x6BFF73 if not response.error else 0x9487F4,
                    prefix="+" if not response.error else "-"
                ))
            except AttributeError:
                continue


def load() -> BaseModule:
    return EmailTracker()


if __name__ == "__main__":
    with load() as module:
        module.run()
