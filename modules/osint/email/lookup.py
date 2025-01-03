import re

import dns.resolver

from utils import log_colorize
from utils.abc import BaseModule
from utils.consts import SCAN_BANNER


class EmailLookup(BaseModule, name="lookup"):

    @staticmethod
    def get_email_info(email: str) -> dict:
        info = {}
        email_parts = email.split('@')
        try:
            info["name"] = email_parts[0]
        except IndexError:
            pass

        domain_mather = re.search(r"@([^@.]+)\.", email)
        if domain_mather:
            info["domain"] = domain_mather.group(1)

        try:
            info["tld"] = f".{email.split('.')[-1]}"
        except IndexError:
            pass

        info["domain_all"] = f"{info.get('domain')}{info.get('tld')}"

        try:
            mx_records = dns.resolver.resolve(info.get("domain_all"), 'MX')
            mx_servers = [str(record.exchange) for record in mx_records]  # noqa
            info["mx_servers"] = mx_servers
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
            pass

        try:
            spf_records = dns.resolver.resolve(info.get("domain_all"), 'SPF')
            info["spf_records"] = [str(record) for record in spf_records]
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
            pass

        try:
            dmarc_records = dns.resolver.resolve(f'_dmarc.{info.get("domain_all")}', 'TXT')
            info["dmarc_records"] = [str(record) for record in dmarc_records]
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
            pass

        if _mx := info.get("mx_servers"):
            for server in _mx:
                if "google.com" in server:
                    info["google_workspace"] = True
                elif "outlook.com" in server:
                    info["microsoft_365"] = True

        return info

    def run(self) -> None:
        self.print_banner(SCAN_BANNER)
        print(log_colorize("Input email address", color=0x5386E5, prefix="<"), end="")
        email = input()

        info = self.get_email_info(email)

        for key, value in info.items():
            if isinstance(value, list):
                print(log_colorize(str(key).upper() + " : " + " / ".join(value), color=0x5386E5, prefix="+"))
            else:
                print(log_colorize(str(key).upper() + " : " + str(value), color=0x5386E5, prefix="+"))


def load() -> BaseModule:
    return EmailLookup()


if __name__ == "__main__":
    with load() as module:
        module: BaseModule
        module.run()
