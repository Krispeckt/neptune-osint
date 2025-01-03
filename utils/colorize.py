__all__ = [
    "hex_to_rgb",
    "colorize",
    "log_colorize",
    "gradient_colorize"
]

from datetime import datetime


def hex_to_rgb(hex_color: int) -> tuple[int, ...]:
    """
    Converts a color in HEX to RGB.

    Parameters
    ----------
        hex_color : int
            color in format 0x000000

    Returns
    -------
        tuple[int, int, int]

    Example
    -------
        >>> hex_to_rgb(0xFF0000)
        (255, 0, 0)
        >>> hex_to_rgb(0x00FF00)
        (0, 255, 0)
        >>> hex_to_rgb(0x0000FF)
        (0, 0, 255)
    """
    # Преобразуем число в шестнадцатеричную строку без префикса '0x'
    hex_color = f"{hex_color:06x}"
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


def colorize(text: str, *, color: int) -> str:
    """
    Returns text colored in 0xRRGGBB format.

    Parameters
    ----------
        text : str
            Colorization text

        color : int
            Color in 0xRRGGBB format.

    Returns
    -------
        str
            Color text using ANSI codes.
    """
    r, g, b = hex_to_rgb(color)
    return f"\033[38;2;{r};{g};{b}m{text}\033[0m"


def log_colorize(text: str, *, color: int, prefix: str) -> str:  # noqa
    """
    Returns text colored in 0xRRGGBB format

    Parameters
    ----------
        text : str
            Colorization text

        color : int
            Color in 0xRRGGBB format.

        prefix : str
            Input prefix.

    Returns
    -------
        str
    """
    _t = datetime.now().strftime("%H:%M:%S")
    return (
        f"{colorize("[", color=color)}{_t}{colorize("]", color=color)} "
        f"{colorize("[", color=color)}{prefix}{colorize("]", color=color)} "
        f"{colorize(text + (" -> " if prefix == "<" else ""), color=color)}"
    )


def gradient_colorize(text: str, *, start_color: int, end_color: int) -> str:
    """
    Returns text colored with a linear gradient.

    Parameters
    ----------
        text : str
            The text to be colorized.

        start_color : int
            Starting color in 0xRRGGBB format.

        end_color : int
            Ending color in 0xRRGGBB format.

    Returns
    -------
        str
            Text with a gradient applied using ANSI codes.
    """
    start_rgb = hex_to_rgb(start_color)
    end_rgb = hex_to_rgb(end_color)

    # Calculate the number of steps based on the length of the text
    steps = len(text)
    gradient_text = []

    for i, char in enumerate(text):
        r = int(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * (i / (steps - 1)))
        g = int(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * (i / (steps - 1)))
        b = int(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * (i / (steps - 1)))

        gradient_text.append(f"\033[38;2;{r};{g};{b}m{char}\033[0m")

    return ''.join(gradient_text)


if __name__ == "__main__":
    print(colorize("Hello, World!", color=0xFF0000))
    print(colorize("Hello, World!", color=0x00FF00))
    print(colorize("Hello, World!", color=0x0000FF))
    print("Hello, World")

    print(gradient_colorize("Hello, World!", start_color=0xFF0000, end_color=0x0000FF))
    print(gradient_colorize("Gradient Text", start_color=0x00FF00, end_color=0xFF00FF))
