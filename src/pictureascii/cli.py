"""PictureASCII conversion logic and command-line interface."""

from argparse import ArgumentParser, BooleanOptionalAction
from pathlib import Path
import os
import re

from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError


# Characters progress from dark on the left to light on the right.
# The backslash is escaped so the palette contains a literal backslash.
ASCII_CHARS = (
    "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/"
    "\\|?-_+~<>i!lI;:,\"^`'.    "
)

DEFAULT_WIDTH = 120

# Compensate for terminal characters being taller than they are wide.
# Decrease this value for tall output or increase it for flat output.
CHAR_ASPECT_RATIO = 0.5

# A value of 1.0 preserves the source RGB values.
DEFAULT_COLOR_SCALE = 1.0

# Most terminals use a dark background, so inversion is enabled by default
# to render bright areas with dense characters. Use --no-invert on light backgrounds.
DEFAULT_INVERT = True

# Font size in points used when rendering images.
DEFAULT_IMAGE_FONT_SIZE = 14

# Padding in pixels inside each character cell in saved PNG files.
DEFAULT_CHARACTER_PADDING = 0

# Pixel dimensions of one ASCII character cell in saved PNG files.
DEFAULT_CHARACTER_CELL_WIDTH = 10
DEFAULT_CHARACTER_CELL_HEIGHT = 14

# Candidate monospace fonts, searched in order. Pillow's default font is used
# when none of these files are available.
MONOSPACE_FONT_CANDIDATES = (
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "/usr/share/fonts/dejavu/DejaVuSansMono.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
    "/System/Library/Fonts/Menlo.ttc",
    "/System/Library/Fonts/Monaco.ttf",
    "C:\\Windows\\Fonts\\consola.ttf",
    "C:\\Windows\\Fonts\\cour.ttf",
)

ANSI_RESET = "\033[0m"

# Matches the 24-bit foreground colors and reset codes produced by rgb_to_ansi().
ANSI_COLOR_PATTERN = re.compile(
    r"\033\[38;2;(\d+);(\d+);(\d+)m|\033\[0m"
)


def enable_windows_ansi() -> None:
    """Enable ANSI color output in Windows consoles that require activation."""
    if os.name == "nt":
        os.system("")


def open_image(image_path: str) -> Image.Image:
    """
    Open an image and convert it to RGB.

    Composite transparent images over white instead of allowing transparent
    pixels to become black during conversion.
    """
    image = Image.open(image_path).convert("RGBA")

    background = Image.new(
        mode="RGBA",
        size=image.size,
        color=(255, 255, 255, 255),
    )

    background.alpha_composite(image)

    return background.convert("RGB")


def resize_image(
    image: Image.Image,
    output_width: int,
    char_aspect_ratio: float = CHAR_ASPECT_RATIO,
) -> Image.Image:
    """Resize an image while preserving its aspect ratio."""
    if output_width < 10:
        raise ValueError(
            "Output width must be at least 10."
        )

    if char_aspect_ratio <= 0:
        raise ValueError(
            "Character aspect-ratio correction must be greater than 0."
        )

    original_width, original_height = image.size

    if original_width <= 0 or original_height <= 0:
        raise ValueError(
            "Image dimensions must be greater than 0."
        )

    image_ratio = original_height / original_width

    output_height = max(
        1,
        round(
            output_width
            * image_ratio
            * char_aspect_ratio
        ),
    )

    return image.resize(
        (output_width, output_height),
        Image.Resampling.LANCZOS,
    )


def brightness_to_character(
    brightness: int,
    invert: bool = False,
    characters: str = ASCII_CHARS,
) -> str:
    """
    Convert a brightness value from 0 to 255 into an ASCII character.

    Zero represents black and 255 represents white.
    """
    characters = (
        characters[::-1]
        if invert
        else characters
    )

    character_index = (
        brightness
        * (len(characters) - 1)
        // 255
    )

    return characters[character_index]


def rgb_to_ansi(
    red: int,
    green: int,
    blue: int,
) -> str:
    """Convert an RGB value into a 24-bit ANSI foreground color code."""
    return f"\033[38;2;{red};{green};{blue}m"


def scale_rgb(
    rgb: tuple[int, int, int],
    color_scale: float,
) -> tuple[int, int, int]:
    """
    Scale RGB brightness by a multiplier.

    1.0 preserves the source color, 0.8 is 20% darker, and 1.1 is 10%
    brighter.
    """
    if color_scale < 0:
        raise ValueError(
            "Color brightness scale must be at least 0."
        )

    red, green, blue = rgb

    red = max(
        0,
        min(255, round(red * color_scale)),
    )
    green = max(
        0,
        min(255, round(green * color_scale)),
    )
    blue = max(
        0,
        min(255, round(blue * color_scale)),
    )

    return red, green, blue


def parse_hex_color(value: str) -> tuple[int, int, int]:
    """Convert a #RGB or #RRGGBB color into an RGB tuple."""
    color = value.lstrip("#")

    if len(color) == 3:
        color = "".join(character * 2 for character in color)

    if len(color) != 6:
        raise ValueError(
            "Color must use the #RGB or #RRGGBB format."
        )

    try:
        return tuple(
            int(color[index:index + 2], 16)
            for index in (0, 2, 4)
        )
    except ValueError as error:
        raise ValueError(
            "Color values may only contain hexadecimal digits (0-9 and A-F)."
        ) from error


def _get_flattened_pixels(image: Image.Image) -> list:
    """Return image pixels using the API available in the installed Pillow."""
    get_flattened_data = getattr(image, "get_flattened_data", None)

    if get_flattened_data is not None:
        return list(get_flattened_data())

    return list(image.getdata())


def image_to_ascii(
    image: Image.Image,
    invert: bool = False,
    color: bool = False,
    color_scale: float = DEFAULT_COLOR_SCALE,
    characters: str = ASCII_CHARS,
) -> str:
    """
    Convert image brightness values into ASCII characters.

    When color is true, apply each resized source pixel's RGB value to its
    corresponding character.

    The image is expected to already be in RGB mode after open_image(). RGB
    pixels are not read when color is false, avoiding unnecessary work.
    """
    grayscale_pixels = _get_flattened_pixels(image.convert("L"))

    rgb_pixels = (
        _get_flattened_pixels(image)
        if color
        else None
    )

    width = image.width
    lines = []

    for start in range(
        0,
        len(grayscale_pixels),
        width,
    ):
        end = start + width

        line_parts = []
        previous_color = None

        for index in range(start, end):
            brightness = grayscale_pixels[index]

            character = brightness_to_character(
                brightness=brightness,
                invert=invert,
                characters=characters,
            )

            if not color:
                line_parts.append(character)
                continue

            current_color = scale_rgb(
                rgb=rgb_pixels[index],
                color_scale=color_scale,
            )

            # Avoid repeating ANSI codes for consecutive characters of one color.
            if current_color != previous_color:
                red, green, blue = current_color

                line_parts.append(
                    rgb_to_ansi(
                        red=red,
                        green=green,
                        blue=blue,
                    )
                )

                previous_color = current_color

            line_parts.append(character)

        if color:
            line_parts.append(ANSI_RESET)

        lines.append("".join(line_parts))

    return "\n".join(lines)


def create_default_output_path(
    image_path: str,
) -> Path:
    """
    Create an output path from the source image name.

    photo.jpg -> photo.txt
    images/cat.png -> images/cat.txt
    """
    return Path(image_path).with_suffix(".txt")


def create_image_output_paths(
    base_path: Path,
) -> tuple[Path, Path]:
    """
    Create output paths for the plain and color PNG variants.

    For a photo.txt base path, return photo_plain.png and photo_color.png.
    """
    stem = base_path.stem
    parent = base_path.parent

    plain_path = parent / f"{stem}_plain.png"
    color_path = parent / f"{stem}_color.png"

    return plain_path, color_path


def load_monospace_font(
    font_size: int,
) -> tuple[ImageFont.ImageFont, bool]:
    """
    Find and load a monospace font from the system.

    Return the font and true when a candidate is available. Return Pillow's
    default font and false when no candidate can be loaded.
    """
    for candidate in MONOSPACE_FONT_CANDIDATES:
        if not Path(candidate).exists():
            continue

        try:
            return ImageFont.truetype(candidate, font_size), True
        except OSError:
            continue

    try:
        return ImageFont.load_default(size=font_size), False
    except TypeError:
        # Older Pillow versions do not accept a size argument for load_default().
        return ImageFont.load_default(), False


def render_ascii_image(
    ascii_text: str,
    output_path: Path,
    background: tuple[int, int, int],
    foreground: tuple[int, int, int] | None,
    target_aspect_ratio: float,
    target_size: tuple[int, int] | None = None,
    font_size: int = DEFAULT_IMAGE_FONT_SIZE,
    character_padding: int = DEFAULT_CHARACTER_PADDING,
    transparent: bool = False,
) -> None:
    """
    Render an ASCII art string as a PNG image.

    A foreground value renders all characters in one color for plain output.
    When foreground is None, parse embedded 24-bit ANSI codes and render each
    character in its source color.
    """
    lines = ascii_text.split("\n")
    plain_lines = [
        ANSI_COLOR_PATTERN.sub("", line) for line in lines
    ]
    max_columns = max(
        (len(line) for line in plain_lines),
        default=0,
    )

    font, is_truetype_font = load_monospace_font(font_size)

    if not is_truetype_font:
        print(
            "Warning: no monospace system font was found. Rendering with "
            "Pillow's default font; character alignment may be inaccurate."
        )

    # Measure the actual glyph bounds to determine the cell size.
    left, top, right, bottom = font.getbbox("M")
    glyph_width = (right - left) or max(1, font_size * 0.6)
    glyph_height = (bottom - top) or font_size
    cell_width = glyph_width + character_padding * 2

    image_width = (
        target_size[0]
        if target_size
        else int(max_columns * cell_width)
    )
    image_height = (
        target_size[1]
        if target_size
        else round(image_width * target_aspect_ratio)
    )
    cell_width = image_width / max(max_columns, 1)
    cell_height = image_height / max(len(lines), 1)

    canvas_mode = "RGBA" if transparent else "RGB"
    canvas_background = (
        (*background, 0)
        if transparent
        else background
    )
    canvas = Image.new(
        canvas_mode,
        (max(image_width, 1), max(image_height, 1)),
        canvas_background,
    )
    draw = ImageDraw.Draw(canvas)

    default_color = foreground or (230, 230, 230)

    for row, line in enumerate(lines):
        x = 0.0
        y = row * cell_height + max(
            character_padding,
            (cell_height - glyph_height) / 2 - top,
        )
        position = 0
        current_color = default_color

        def draw_characters(text: str) -> None:
            nonlocal x

            for character in text:
                character_left, _, character_right, _ = font.getbbox(character)
                character_width = character_right - character_left
                draw.text(
                    (x + (cell_width - character_width) / 2 - character_left, y),
                    character,
                    fill=current_color,
                    font=font,
                )
                x += cell_width

        for match in ANSI_COLOR_PATTERN.finditer(line):
            text_segment = line[position:match.start()]

            if text_segment:
                draw_characters(text_segment)

            # Ignore ANSI codes in plain output with an explicit foreground.
            if foreground is None:
                if match.group(1):
                    current_color = (
                        int(match.group(1)),
                        int(match.group(2)),
                        int(match.group(3)),
                    )
                else:
                    current_color = default_color

            position = match.end()

        remaining_text = line[position:]

        if remaining_text:
            draw_characters(remaining_text)

    canvas.save(output_path)


def save_ascii_images(
    source_image: Image.Image,
    output_width: int,
    output_txt_path: Path,
    invert: bool,
    color: bool,
    target_aspect_ratio: float,
    color_scale: float = DEFAULT_COLOR_SCALE,
    font_size: int = DEFAULT_IMAGE_FONT_SIZE,
    characters: str = ASCII_CHARS,
    cell_width: int = DEFAULT_CHARACTER_CELL_WIDTH,
    cell_height: int = DEFAULT_CHARACTER_CELL_HEIGHT,
    image_width: int | None = None,
    image_height: int | None = None,
    background_color: tuple[int, int, int] | None = None,
    foreground_color: tuple[int, int, int] | None = None,
    transparent: bool = False,
) -> Path:
    """
    Save one plain or color PNG according to the color setting.

    Return the path of the saved image.
    """
    if image_width is not None and image_width <= 0:
        raise ValueError("Saved image width must be at least 1.")
    if image_height is not None and image_height <= 0:
        raise ValueError("Saved image height must be at least 1.")
    if cell_width <= 0 or cell_height <= 0:
        raise ValueError("Character cell dimensions must be at least 1.")

    if image_width is not None and image_height is not None:
        target_size = (image_width, image_height)
    elif image_width is not None:
        target_size = (
            image_width,
            max(1, round(image_width * target_aspect_ratio)),
        )
    elif image_height is not None:
        target_size = (
            max(1, round(image_height / target_aspect_ratio)),
            image_height,
        )
    else:
        target_size = None

    rendering_aspect_ratio = (
        target_size[1] / target_size[0]
        if target_size
        else target_aspect_ratio
    )
    output_height = max(
        1,
        round(
            output_width
            * rendering_aspect_ratio
            * cell_width
            / cell_height
        ),
    )
    image_for_rendering = source_image.resize(
        (output_width, output_height),
        Image.Resampling.LANCZOS,
    )

    ascii_art = image_to_ascii(
        image=image_for_rendering,
        invert=invert,
        color=color,
        color_scale=color_scale,
        characters=characters,
    )

    # Match inverted output to a dark background with light text. Non-inverted
    # output uses a light background with dark text.
    if invert:
        background = (18, 18, 18)
        foreground = (230, 230, 230)
    else:
        background = (255, 255, 255)
        foreground = (20, 20, 20)

    background = background_color or background
    foreground = foreground_color or foreground

    plain_image_path, color_image_path = create_image_output_paths(
        base_path=output_txt_path
    )

    output_path = color_image_path if color else plain_image_path

    render_ascii_image(
        ascii_text=ascii_art,
        output_path=output_path,
        background=background,
        foreground=None if color else foreground,
        target_aspect_ratio=rendering_aspect_ratio,
        target_size=target_size or (
            output_width * cell_width,
            output_height * cell_height,
        ),
        font_size=font_size,
        transparent=transparent,
    )

    return output_path


def convert_image_to_ascii(
    image_path: str,
    output_path: str | Path,
    width: int = DEFAULT_WIDTH,
    char_aspect_ratio: float = CHAR_ASPECT_RATIO,
    invert: bool = DEFAULT_INVERT,
    color: bool = False,
    color_scale: float = DEFAULT_COLOR_SCALE,
    save_image: bool = False,
    image_font_size: int = DEFAULT_IMAGE_FONT_SIZE,
    characters: str = ASCII_CHARS,
    cell_width: int = DEFAULT_CHARACTER_CELL_WIDTH,
    cell_height: int = DEFAULT_CHARACTER_CELL_HEIGHT,
    image_width: int | None = None,
    image_height: int | None = None,
    background_color: tuple[int, int, int] | None = None,
    foreground_color: tuple[int, int, int] | None = None,
    transparent: bool = False,
) -> tuple[str, Path | None, Path | None]:
    """
    Convert an image into ASCII art.

    Terminal output may contain color, but the TXT file always contains plain
    ASCII without ANSI codes.

    When save_image is true, also save a PNG matching the color setting.

    Return terminal text, the optional plain image path, and the optional color
    image path.
    """
    image = open_image(image_path)

    if not characters:
        raise ValueError("ASCII character palette cannot be empty.")

    if save_image:
        if cell_width <= 0 or cell_height <= 0:
            raise ValueError("Character cell dimensions must be at least 1.")
        if image_font_size <= 0:
            raise ValueError("Saved image font size must be at least 1.")
        if image_width is not None and image_width <= 0:
            raise ValueError("Saved image width must be at least 1.")
        if image_height is not None and image_height <= 0:
            raise ValueError("Saved image height must be at least 1.")

    resized_image = resize_image(
        image=image,
        output_width=width,
        char_aspect_ratio=char_aspect_ratio,
    )

    # Plain ASCII art written to the text file.
    plain_ascii_art = image_to_ascii(
        image=resized_image,
        invert=invert,
        color=False,
        characters=characters,
    )

    # Reuse plain output for the terminal unless color rendering is requested.
    terminal_ascii_art = (
        plain_ascii_art
        if not color
        else image_to_ascii(
            image=resized_image,
            invert=invert,
            color=True,
            color_scale=color_scale,
            characters=characters,
        )
    )

    output_file = Path(output_path)

    output_file.write_text(
        plain_ascii_art,
        encoding="utf-8",
    )

    plain_image_path = None
    color_image_path = None

    if save_image:
        saved_image_path = save_ascii_images(
            source_image=image,
            output_width=resized_image.width,
            output_txt_path=output_file,
            invert=invert,
            color=color,
            target_aspect_ratio=image.height / image.width,
            color_scale=color_scale,
            font_size=image_font_size,
            characters=characters,
            cell_width=cell_width,
            cell_height=cell_height,
            image_width=image_width,
            image_height=image_height,
            background_color=background_color,
            foreground_color=foreground_color,
            transparent=transparent,
        )

        if color:
            color_image_path = saved_image_path
        else:
            plain_image_path = saved_image_path

    return terminal_ascii_art, plain_image_path, color_image_path


def create_parser() -> ArgumentParser:
    parser = ArgumentParser(
        description="Convert an image into ASCII art while preserving its aspect ratio."
    )

    parser.add_argument(
        "image",
        help="Path to the image file to convert.",
    )

    parser.add_argument(
        "-w",
        "--width",
        type=int,
        default=DEFAULT_WIDTH,
        help=(
            f"Number of characters per output row (default: {DEFAULT_WIDTH})."
        ),
    )

    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help=(
            "Path for the output text file. By default, the input filename "
            "is used with a .txt extension."
        ),
    )

    parser.add_argument(
        "--ratio",
        "--terminal-ratio",
        dest="ratio",
        type=float,
        default=CHAR_ASPECT_RATIO,
        help=(
            "Terminal and TXT character aspect-ratio correction factor; "
            "saved PNG proportions use the configured character cell size "
            f"(default: {CHAR_ASPECT_RATIO})."
        ),
    )

    parser.add_argument(
        "--invert",
        action=BooleanOptionalAction,
        default=DEFAULT_INVERT,
        help=(
            "Invert the character brightness mapping for dark terminal "
            "backgrounds. Use --no-invert for a light background."
        ),
    )

    parser.add_argument(
        "--color",
        action="store_true",
        help=(
            "Apply the source image's RGB colors to terminal characters."
        ),
    )

    parser.add_argument(
        "--color-scale",
        type=float,
        default=None,
        help=(
            "Color brightness multiplier. 1.0 preserves the source colors; "
            "0.8 makes them 20%% darker "
            f"(default: {DEFAULT_COLOR_SCALE})."
        ),
    )

    parser.add_argument(
        "--save-image",
        action="store_true",
        help=(
            "Also save the ASCII art as a PNG. Saves *_color.png with "
            "--color, otherwise *_plain.png."
        ),
    )

    parser.add_argument(
        "--image-font-size",
        type=int,
        default=None,
        help=(
            "Font size used to render saved PNG files "
            f"(default: {DEFAULT_IMAGE_FONT_SIZE})."
        ),
    )

    parser.add_argument(
        "--cell-width",
        type=int,
        default=None,
        help=f"Character cell width in saved PNG files (default: {DEFAULT_CHARACTER_CELL_WIDTH}).",
    )

    parser.add_argument(
        "--cell-height",
        type=int,
        default=None,
        help=f"Character cell height in saved PNG files (default: {DEFAULT_CHARACTER_CELL_HEIGHT}).",
    )

    parser.add_argument(
        "--chars",
        default=ASCII_CHARS,
        help="Character palette used to represent brightness levels.",
    )

    parser.add_argument(
        "--background",
        default=None,
        help="Background color for saved PNG files (#RGB or #RRGGBB).",
    )

    parser.add_argument(
        "--foreground",
        default=None,
        help="Text color for plain saved PNG files (#RGB or #RRGGBB).",
    )

    parser.add_argument(
        "--transparent",
        action="store_true",
        help="Make the background of saved PNG files transparent.",
    )

    parser.add_argument(
        "--image-width",
        type=int,
        default=None,
        help="Exact width of the saved PNG in pixels.",
    )

    parser.add_argument(
        "--image-height",
        type=int,
        default=None,
        help="Exact height of the saved PNG in pixels.",
    )

    return parser


def main() -> None:
    parser = create_parser()
    args = parser.parse_args()

    png_only_options = []

    if args.image_font_size is not None:
        png_only_options.append("--image-font-size")
    if args.cell_width is not None:
        png_only_options.append("--cell-width")
    if args.cell_height is not None:
        png_only_options.append("--cell-height")
    if args.background:
        png_only_options.append("--background")
    if args.foreground:
        png_only_options.append("--foreground")
    if args.transparent:
        png_only_options.append("--transparent")
    if args.image_width is not None:
        png_only_options.append("--image-width")
    if args.image_height is not None:
        png_only_options.append("--image-height")

    if png_only_options and not args.save_image:
        option_label = ", ".join(png_only_options)
        requirement = "requires" if len(png_only_options) == 1 else "require"
        parser.error(
            f"{option_label} {requirement} --save-image"
        )

    if args.foreground and args.color:
        parser.error(
            "--foreground cannot be used with --color because colored output "
            "uses the source image's RGB values"
        )

    if args.background and args.transparent:
        parser.error(
            "--background cannot be used with --transparent because the "
            "background is fully transparent"
        )

    if args.color_scale is not None and not args.color:
        parser.error("--color-scale requires --color")

    color_scale = (
        args.color_scale
        if args.color_scale is not None
        else DEFAULT_COLOR_SCALE
    )
    image_font_size = (
        args.image_font_size
        if args.image_font_size is not None
        else DEFAULT_IMAGE_FONT_SIZE
    )
    cell_width = (
        args.cell_width
        if args.cell_width is not None
        else DEFAULT_CHARACTER_CELL_WIDTH
    )
    cell_height = (
        args.cell_height
        if args.cell_height is not None
        else DEFAULT_CHARACTER_CELL_HEIGHT
    )

    output_path = (
        Path(args.output)
        if args.output
        else create_default_output_path(args.image)
    )

    if args.color:
        enable_windows_ansi()

    try:
        background_color = (
            parse_hex_color(args.background)
            if args.background
            else None
        )
        foreground_color = (
            parse_hex_color(args.foreground)
            if args.foreground
            else None
        )

        (
            terminal_ascii_art,
            plain_image_path,
            color_image_path,
        ) = convert_image_to_ascii(
            image_path=args.image,
            output_path=output_path,
            width=args.width,
            char_aspect_ratio=args.ratio,
            invert=args.invert,
            color=args.color,
            color_scale=color_scale,
            save_image=args.save_image,
            image_font_size=image_font_size,
            characters=args.chars,
            cell_width=cell_width,
            cell_height=cell_height,
            image_width=args.image_width,
            image_height=args.image_height,
            background_color=background_color,
            foreground_color=foreground_color,
            transparent=args.transparent,
        )

    except FileNotFoundError:
        print(
            "Error: image file not found: "
            f"{args.image}"
        )
        raise SystemExit(1)

    except UnidentifiedImageError:
        print(
            "Error: the image file is unsupported or corrupted."
        )
        raise SystemExit(1)

    except PermissionError:
        print(
            "Error: permission denied for the image or output file."
        )
        raise SystemExit(1)

    except (OSError, ValueError) as error:
        print(f"Error: {error}")
        raise SystemExit(1)

    print(terminal_ascii_art)

    if args.color:
        print(ANSI_RESET, end="")

    print()
    print(
        f"Saved the result to '{output_path}'."
    )

    if args.save_image:
        saved_image_path = color_image_path or plain_image_path
        print(f"Saved image: '{saved_image_path}'")


if __name__ == "__main__":
    main()
