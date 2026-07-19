# Picture ASCII

**English** | [한국어](i18n/README.ko.md) | [日本語](i18n/README.ja.md) | [Español](i18n/README.es.md) | [Français](i18n/README.fr.md)

A Python program that converts images into ASCII characters.

- Plain ASCII text output
- Terminal output using the source image's RGB colors
- Plain or color PNG export
- Custom character palettes, cell sizes, backgrounds, and foreground colors
- Transparent backgrounds and configurable PNG dimensions

## Samples

- [Source image](https://github.com/doyeon789/pictureascii/tree/main/example/images/sample.png)
- [ASCII text (the aspect ratio may differ because of GitHub font rendering)](https://github.com/doyeon789/pictureascii/tree/main/example/outputs/sample.txt)
- [Plain ASCII image](https://github.com/doyeon789/pictureascii/tree/main/example/outputs/sample_plain.png)
- [Color ASCII image](https://github.com/doyeon789/pictureascii/tree/main/example/outputs/sample_color.png)

## Installation

Python 3.10 or later is required.

```bash
pip install pictureascii
```

For local development, run this command from the project root:

```bash
python -m pip install -e .
```

## Basic Usage

```bash
pascii picture.png
```

`pascii` is the short alias for `pictureascii`; both commands behave identically. The output is saved as `picture.txt` next to the source image. Change the output width with `--width`:

```bash
pascii picture.png --width 200
```

## Color Output

Apply the source image's RGB colors to each character:

```bash
pascii picture.png --color
pascii picture.png --color --color-scale 0.8
```

Color terminal output works best in a terminal with 24-bit ANSI color support, such as Windows Terminal or PowerShell.

`--color-scale` requires `--color`.

## PNG Export

```bash
pascii picture.png --save-image
pascii picture.png --color --save-image
```

Generated files use these names:

```text
picture.txt
picture_plain.png   # --save-image
picture_color.png   # --color --save-image
```

The TXT file contains plain ASCII characters without ANSI color codes.
PNG-specific options require `--save-image`.

## Terminal Aspect Ratio

Use `--terminal-ratio` to adjust the character aspect ratio in terminal and
TXT output. The shorter `--ratio` name remains available and behaves
identically.

```bash
pictureascii picture.png --terminal-ratio 0.6
```

This setting does not control saved PNG proportions. PNG output uses its
configured character cell size.

## Cell Size

The default size of one ASCII character cell in a PNG is `10x14px`.

```bash
pictureascii picture.png --cell-width 8 --cell-height 12 --image-font-size 10 --save-image
```

Unless explicit PNG dimensions are provided, the size is calculated as follows:

```text
PNG width  = number of columns x cell width
PNG height = number of rows x cell height
```

`--image-font-size` controls the actual font size inside each cell. Choose a
font size that fits the configured cell dimensions to avoid clipped or
overlapping characters.

## Character Palette

Use `--chars` to define the characters used for brightness levels. The leftmost character represents dark areas and the rightmost character represents bright areas.

```bash
pictureascii picture.png --chars "@%#*+=-:. "
```

Keep the space at the end of the palette for a natural brightness transition.

## Background And Foreground

Colors accept `#RGB` or `#RRGGBB` values.

```bash
pascii picture.png --background "#101820" --foreground "#F2AA4C" --save-image
```

`--foreground` controls text color for plain PNG output. It cannot be combined
with `--color`, because colored output uses the source image's RGB values.

## Transparent Background

```bash
pascii picture.png --transparent --save-image
pascii picture.png --color --transparent --save-image
```

`--transparent` cannot be combined with `--background`.

## PNG Dimensions

Set the output PNG dimensions directly:

```bash
pascii picture.png --image-width 1200 --image-height 800 --save-image
```

- When both dimensions are set, the image is saved at that exact size.
- When only one dimension is set, the other is calculated from the source aspect ratio.
- When neither is set, the dimensions are calculated from the character count and cell size.

## Complete Example

```bash
pascii picture.png --color --width 180 --chars "@%#*+=-:. " --cell-width 10 --cell-height 14 --image-width 1800 --transparent --save-image
```

## Options

| Option | Description | Default |
|---|---|---:|
| `image` | Path to the source image | Required |
| `-w`, `--width` | Number of output columns | `120` |
| `-o`, `--output` | TXT output path | Source name with `.txt` |
| `--ratio`, `--terminal-ratio` | Terminal and TXT character aspect-ratio correction | `0.5` |
| `--invert`, `--no-invert` | Invert character brightness | Enabled |
| `--color` | Apply source RGB colors to characters | Disabled |
| `--color-scale` | Color brightness multiplier; requires `--color` | `1.0` |
| `--save-image` | Save the current output mode as PNG | Disabled |
| `--image-font-size` | Font size used in saved PNG files | `14` |
| `--cell-width` | Character cell width | `10` |
| `--cell-height` | Character cell height | `14` |
| `--chars` | Character palette | Built-in palette |
| `--background` | PNG background color; incompatible with `--transparent` | Automatic |
| `--foreground` | Plain PNG text color; incompatible with `--color` | Automatic |
| `--transparent` | Use a transparent PNG background; incompatible with `--background` | Disabled |
| `--image-width` | PNG width | Automatic |
| `--image-height` | PNG height | Automatic |

View the full command help:

```bash
pascii --help
```

You can also run the package as a module:

```bash
python -m pictureascii picture.png --color
```

## Development And Release

Run the tests:

```bash
python -m unittest discover -s tests -v
```

Build and validate the distributions:

```bash
python -m pip install --upgrade build twine
python -m build
python -m twine check dist/*
```

Publish to TestPyPI first, then publish the verified release to PyPI:

```bash
python -m twine upload --repository testpypi dist/*
python -m twine upload dist/*
```

Before releasing a new version, update the version in both `pyproject.toml` and `src/pictureascii/__init__.py`, then rebuild `dist`.
