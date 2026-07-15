"""PictureASCII conversion logic and command-line interface."""

from argparse import ArgumentParser, BooleanOptionalAction
from pathlib import Path
import os
import re

from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError


# 왼쪽일수록 어둡고, 오른쪽일수록 밝게 보이는 문자
# 문자열에 실제 역슬래시(\)를 넣기 위해 "\\"로 작성합니다.
ASCII_CHARS = (
    "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/"
    "\\|?-_+~<>i!lI;:,\"^`'.    "
)

DEFAULT_WIDTH = 120

# 터미널 문자는 일반적으로 세로가 더 길기 때문에 높이를 보정합니다.
# 결과가 세로로 길면 줄이고, 너무 납작하면 늘리세요.
CHAR_ASPECT_RATIO = 0.5

# 1.0이면 원본 RGB를 그대로 사용합니다.
DEFAULT_COLOR_SCALE = 1.0

# 대부분의 터미널은 어두운 배경을 기본으로 쓰기 때문에,
# 밝은 부분이 촘촘한 문자로 채워지도록 기본값을 반전(True)으로 둡니다.
# 밝은 배경 터미널을 쓴다면 --no-invert로 끄세요.
DEFAULT_INVERT = True

# 이미지로 저장할 때 사용하는 폰트 크기(포인트 단위)입니다.
DEFAULT_IMAGE_FONT_SIZE = 14

# PNG로 저장할 때 각 문자 셀 안에 둘 여백(픽셀)입니다.
DEFAULT_CHARACTER_PADDING = 0

# 저장 PNG에서 ASCII 문자 하나가 차지하는 픽셀 셀 크기입니다.
DEFAULT_CHARACTER_CELL_WIDTH = 10
DEFAULT_CHARACTER_CELL_HEIGHT = 14

# 이미지 렌더링에 사용할 모노스페이스 폰트 후보 경로입니다.
# 위에서부터 순서대로 찾아보고, 하나도 없으면 PIL 기본 폰트로 대체합니다.
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

# rgb_to_ansi()가 만드는 24비트 전경색 코드와 리셋 코드를 다시 읽어내기 위한 패턴입니다.
ANSI_COLOR_PATTERN = re.compile(
    r"\033\[38;2;(\d+);(\d+);(\d+)m|\033\[0m"
)


def enable_windows_ansi() -> None:
    """
    일부 Windows 콘솔에서 ANSI 색상 출력을 활성화합니다.
    """
    if os.name == "nt":
        os.system("")


def open_image(image_path: str) -> Image.Image:
    """
    이미지 파일을 열고 RGB 형식으로 변환합니다.

    투명한 PNG 이미지는 검은색이 아니라
    흰색 배경 위에 합성합니다.
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
    """
    원본 이미지의 비율을 유지하면서 크기를 조절합니다.
    """
    if output_width < 10:
        raise ValueError(
            "출력 가로 크기는 10 이상이어야 합니다."
        )

    if char_aspect_ratio <= 0:
        raise ValueError(
            "문자 비율 보정값은 0보다 커야 합니다."
        )

    original_width, original_height = image.size

    if original_width <= 0 or original_height <= 0:
        raise ValueError(
            "이미지 크기가 올바르지 않습니다."
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
    0~255 범위의 밝기를 아스키 문자로 변환합니다.

    0은 검은색이고 255는 흰색입니다.
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
    """
    RGB 값을 ANSI 24비트 전경색 코드로 변환합니다.
    """
    return f"\033[38;2;{red};{green};{blue}m"


def scale_rgb(
    rgb: tuple[int, int, int],
    color_scale: float,
) -> tuple[int, int, int]:
    """
    RGB 밝기를 배율에 따라 조절합니다.

    1.0: 원본 색상
    0.8: 원본보다 20% 어둡게
    1.1: 원본보다 10% 밝게
    """
    if color_scale < 0:
        raise ValueError(
            "색상 밝기 배율은 0 이상이어야 합니다."
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
    """#RGB 또는 #RRGGBB 형식의 색상을 RGB 튜플로 변환합니다."""
    color = value.lstrip("#")

    if len(color) == 3:
        color = "".join(character * 2 for character in color)

    if len(color) != 6:
        raise ValueError(
            "색상은 #RGB 또는 #RRGGBB 형식이어야 합니다."
        )

    try:
        return tuple(
            int(color[index:index + 2], 16)
            for index in (0, 2, 4)
        )
    except ValueError as error:
        raise ValueError(
            "색상에는 0~9와 A~F만 사용할 수 있습니다."
        ) from error


def image_to_ascii(
    image: Image.Image,
    invert: bool = False,
    color: bool = False,
    color_scale: float = DEFAULT_COLOR_SCALE,
    characters: str = ASCII_CHARS,
) -> str:
    """
    이미지의 밝기를 아스키 문자로 변환합니다.

    color=True일 때는 축소된 원본 이미지의
    RGB 색상을 각 문자에 그대로 적용합니다.

    image는 이미 RGB 모드로 전달된다고 가정합니다
    (open_image에서 변환이 끝난 상태).
    color=False일 때는 RGB 픽셀을 읽지 않아
    불필요한 연산을 피합니다.
    """
    grayscale_pixels = list(
        image.convert("L").getdata()
    )

    rgb_pixels = (
        list(image.getdata())
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

            # 같은 색이 연속될 때 ANSI 코드를 반복하지 않습니다.
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
    원본 이미지 이름으로 출력 파일 경로를 만듭니다.

    photo.jpg -> photo.txt
    images/cat.png -> images/cat.txt
    """
    return Path(image_path).with_suffix(".txt")


def create_image_output_paths(
    base_path: Path,
) -> tuple[Path, Path]:
    """
    이미지로 저장할 때 사용할 (일반 버전, 컬러 버전) 경로를 만듭니다.

    base_path가 photo.txt라면
    photo_plain.png, photo_color.png를 반환합니다.
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
    시스템에서 모노스페이스 폰트를 찾아 불러옵니다.

    사용 가능한 폰트를 찾으면 (폰트, True)를,
    하나도 찾지 못해 PIL 기본 폰트로 대체하면
    (폰트, False)를 반환합니다.
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
        # 오래된 Pillow 버전은 load_default()에 size 인자를 지원하지 않습니다.
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
    아스키 아트 문자열을 PNG 이미지로 렌더링합니다.

    foreground를 지정하면 모든 글자를 그 색 하나로 그립니다(일반 버전용).
    foreground가 None이면 문자열에 포함된 ANSI 24비트 색상 코드를
    해석해서 각 글자를 원본 색상 그대로 그립니다(컬러 버전용).
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

    if target_size and max_columns and lines:
        left, top, right, bottom = font.getbbox("M")
        base_width = (right - left) or max(1, font_size * 0.6)
        base_height = (bottom - top) or font_size
        target_cell_width = target_size[0] / max_columns
        target_cell_height = target_size[1] / len(lines)
        font_scale = min(
            target_cell_width / (base_width + character_padding * 2),
            target_cell_height / (base_height + character_padding * 2),
        )
        scaled_font_size = max(1, round(font_size * font_scale))
        font, is_truetype_font = load_monospace_font(scaled_font_size)

    if not is_truetype_font:
        print(
            "경고: 시스템에서 모노스페이스 폰트를 찾지 못해 "
            "기본 폰트로 이미지를 렌더링합니다. 글자 정렬이 "
            "다소 어긋날 수 있습니다."
        )

    # 폰트의 실제 글자 크기를 측정해 셀 크기를 정합니다.
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

            # foreground가 지정된 일반 버전에서는 ANSI 코드를 무시합니다.
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
    color 설정에 맞는 일반 또는 컬러 PNG 이미지 하나를 저장합니다.

    반환값은 저장된 이미지 경로입니다.
    """
    if image_width is not None and image_width <= 0:
        raise ValueError("저장 이미지 너비는 1 이상이어야 합니다.")
    if image_height is not None and image_height <= 0:
        raise ValueError("저장 이미지 높이는 1 이상이어야 합니다.")
    if cell_width <= 0 or cell_height <= 0:
        raise ValueError("문자 셀 크기는 1 이상이어야 합니다.")

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

    # invert=True는 어두운 터미널 배경을 가정하므로
    # 이미지도 어두운 배경 + 밝은 글자로 맞춥니다.
    # invert=False는 반대로 밝은 배경 + 어두운 글자를 씁니다.
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
    이미지를 아스키 아트로 변환합니다.

    터미널에는 컬러 결과를 출력할 수 있지만,
    txt 파일에는 ANSI 코드가 없는 일반 결과를 저장합니다.

    save_image=True이면 color 설정에 맞는 PNG 이미지도 함께 저장합니다.

    반환값은 (터미널 출력용 문자열, 일반 이미지 경로 또는 None,
    컬러 이미지 경로 또는 None)입니다.
    """
    image = open_image(image_path)

    if not characters:
        raise ValueError("ASCII 문자 팔레트는 비어 있을 수 없습니다.")

    if save_image:
        if cell_width <= 0 or cell_height <= 0:
            raise ValueError("문자 셀 크기는 1 이상이어야 합니다.")
        if image_font_size <= 0:
            raise ValueError("저장 이미지 폰트 크기는 1 이상이어야 합니다.")
        if image_width is not None and image_width <= 0:
            raise ValueError("저장 이미지 너비는 1 이상이어야 합니다.")
        if image_height is not None and image_height <= 0:
            raise ValueError("저장 이미지 높이는 1 이상이어야 합니다.")

    resized_image = resize_image(
        image=image,
        output_width=width,
        char_aspect_ratio=char_aspect_ratio,
    )

    # 텍스트 파일에 저장할 일반 아스키 아트
    plain_ascii_art = image_to_ascii(
        image=resized_image,
        invert=invert,
        color=False,
        characters=characters,
    )

    # 터미널에 출력할 결과.
    # color=False라면 plain_ascii_art와 완전히 동일하므로
    # 다시 계산하지 않고 그대로 재사용합니다.
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
        type=float,
        default=CHAR_ASPECT_RATIO,
        help=(
            "Character aspect-ratio correction factor "
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
        default=DEFAULT_COLOR_SCALE,
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
        default=DEFAULT_IMAGE_FONT_SIZE,
        help=(
            "Base font size used to render saved PNG files "
            f"(default: {DEFAULT_IMAGE_FONT_SIZE})."
        ),
    )

    parser.add_argument(
        "--cell-width",
        type=int,
        default=DEFAULT_CHARACTER_CELL_WIDTH,
        help=f"Character cell width in saved PNG files (default: {DEFAULT_CHARACTER_CELL_WIDTH}).",
    )

    parser.add_argument(
        "--cell-height",
        type=int,
        default=DEFAULT_CHARACTER_CELL_HEIGHT,
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
            color_scale=args.color_scale,
            save_image=args.save_image,
            image_font_size=args.image_font_size,
            characters=args.chars,
            cell_width=args.cell_width,
            cell_height=args.cell_height,
            image_width=args.image_width,
            image_height=args.image_height,
            background_color=background_color,
            foreground_color=foreground_color,
            transparent=args.transparent,
        )

    except FileNotFoundError:
        print(
            "오류: 이미지 파일을 찾을 수 없습니다: "
            f"{args.image}"
        )
        raise SystemExit(1)

    except UnidentifiedImageError:
        print(
            "오류: 지원하지 않거나 "
            "손상된 이미지 파일입니다."
        )
        raise SystemExit(1)

    except PermissionError:
        print(
            "오류: 이미지 또는 출력 파일에 "
            "접근할 권한이 없습니다."
        )
        raise SystemExit(1)

    except (OSError, ValueError) as error:
        print(f"오류: {error}")
        raise SystemExit(1)

    print(terminal_ascii_art)

    if args.color:
        print(ANSI_RESET, end="")

    print()
    print(
        f"결과를 '{output_path}' 파일에 저장했습니다."
    )

    if args.save_image:
        saved_image_path = color_image_path or plain_image_path
        print(f"저장한 이미지: '{saved_image_path}'")


if __name__ == "__main__":
    main()
