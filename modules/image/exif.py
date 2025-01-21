from json import loads, JSONDecodeError
from os.path import isfile
from pyexiv2 import Image

from utils import log_colorize, colorize
from utils.abc import BaseModule
from utils.consts.banners import EXIF_BANNER


class Exif(BaseModule, name='exif'):

    @staticmethod
    def __print_formatted_exif(exif: dict) -> None:
        for key, value in exif.items():
            try:
                value_to_dict: dict = loads(value)
                if isinstance(value_to_dict, dict):
                    value = ', '.join(f'{key}: {value}' for key, value in value_to_dict.items())
            except JSONDecodeError:
                pass

            print(log_colorize(key.upper() + " : " + str(value), color=0x5386E5, prefix="+"))

    @staticmethod
    def exif_clear(img_path: str) -> None:
        with Image(img_path) as img:
            img.clear_exif()

        print(log_colorize('EXIF cleared', color=0x5386E5, prefix=">"))

    def exif_read(self, img_path: str) -> None:
        with Image(img_path) as img:
            data: dict = img.read_exif()

        if not data:
            return print(log_colorize('EXIF not found', color=0x9487F4, prefix=">"))

        self.__print_formatted_exif(exif=data)

    def run(self) -> None:
        self.print_banner(EXIF_BANNER)
        print(log_colorize("Input image path: ", color=0x5386E5, prefix="<"), end="")

        img_path: str = input()

        if not isfile(img_path):
            return print(log_colorize('File not found', color=0x9487F4, prefix=">"))

        print(colorize("\n>          Read EXIF (#1)", color=0x5386E5))
        print(colorize(">          Clear EXIF (#2)\n", color=0x5386E5))
        print(log_colorize("Choice", color=0x5386E5, prefix="<"), end="")

        choice: str = input().strip()

        match choice:
            case '1':
                self.exif_read(img_path)
            case '2':
                self.exif_clear(img_path)
            case _:
                print(log_colorize("Invalid choice", color=0x9487F4, prefix=">"))


def load() -> BaseModule:
    return Exif()


if __name__ == "__main__":
    with load() as module:
        module: BaseModule
        module.run()
