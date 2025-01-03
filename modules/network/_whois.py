from whois import whois

from utils import log_colorize, gradient_colorize
from utils.abc import BaseModule
from utils.consts import SCAN_BANNER


class Whois(BaseModule, name="whois"):

    @staticmethod
    def ask_domain() -> str:
        print(log_colorize("Input network url", color=0x5386E5, prefix="<"), end="")
        return input()

    @classmethod
    def run(cls) -> None:
        cls.print_banner(SCAN_BANNER)
        domain = cls.ask_domain()

        print(log_colorize(f"Scanning website {domain}...", color=0x5386E5, prefix=">"))

        for key, value in whois(domain).items():
            print(f"{log_colorize(key.capitalize() + ":", color=0x5386E5, prefix="+")} {value}")


def load() -> BaseModule:
    return Whois()


if __name__ == "__main__":
    with load() as module:
        module: BaseModule
        module.run()
