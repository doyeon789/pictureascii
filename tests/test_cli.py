from pathlib import Path
from tempfile import TemporaryDirectory
from contextlib import redirect_stderr
from io import StringIO
from unittest.mock import patch
import unittest

from PIL import Image, ImageChops

from pictureascii.cli import convert_image_to_ascii, main


class ConvertImageTests(unittest.TestCase):
    def test_plain_text_and_png_are_created(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source_path = root / "source.png"
            output_path = root / "result.txt"
            Image.new("RGB", (20, 10), (120, 80, 40)).save(source_path)

            _, plain_path, color_path = convert_image_to_ascii(
                image_path=str(source_path),
                output_path=output_path,
                width=10,
                save_image=True,
            )

            self.assertTrue(output_path.exists())
            self.assertTrue(plain_path and plain_path.exists())
            self.assertIsNone(color_path)

    def test_colored_transparent_png_has_requested_size(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source_path = root / "source.png"
            output_path = root / "result.txt"
            Image.new("RGB", (20, 10), (120, 80, 40)).save(source_path)

            _, _, color_path = convert_image_to_ascii(
                image_path=str(source_path),
                output_path=output_path,
                width=10,
                color=True,
                save_image=True,
                transparent=True,
                image_width=100,
                image_height=50,
            )

            self.assertTrue(color_path)
            with Image.open(color_path) as output_image:
                self.assertEqual(output_image.size, (100, 50))
                self.assertEqual(output_image.mode, "RGBA")

    def test_image_font_size_changes_saved_png_rendering(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source_path = root / "source.png"
            Image.new("RGB", (20, 10), (120, 80, 40)).save(source_path)

            output_paths = []

            for font_size in (8, 24):
                output_path = root / f"result-{font_size}.txt"
                _, plain_path, _ = convert_image_to_ascii(
                    image_path=str(source_path),
                    output_path=output_path,
                    width=10,
                    save_image=True,
                    image_font_size=font_size,
                )
                self.assertIsNotNone(plain_path)
                output_paths.append(plain_path)

            with (
                Image.open(output_paths[0]) as small_font_image,
                Image.open(output_paths[1]) as large_font_image,
            ):
                difference = ImageChops.difference(
                    small_font_image,
                    large_font_image,
                )
                self.assertIsNotNone(difference.getbbox())

    def test_png_only_option_requires_save_image(self) -> None:
        with patch(
            "sys.argv",
            ["pascii", "source.png", "--background", "#fff"],
        ):
            with redirect_stderr(StringIO()):
                with self.assertRaises(SystemExit) as error:
                    main()

        self.assertEqual(error.exception.code, 2)

    def test_foreground_cannot_be_used_with_color(self) -> None:
        with patch(
            "sys.argv",
            [
                "pascii",
                "source.png",
                "--save-image",
                "--color",
                "--foreground",
                "#fff",
            ],
        ):
            with redirect_stderr(StringIO()):
                with self.assertRaises(SystemExit) as error:
                    main()

        self.assertEqual(error.exception.code, 2)

    def test_color_scale_requires_color(self) -> None:
        with patch(
            "sys.argv",
            ["pascii", "source.png", "--color-scale", "0.8"],
        ):
            with redirect_stderr(StringIO()):
                with self.assertRaises(SystemExit) as error:
                    main()

        self.assertEqual(error.exception.code, 2)

    def test_background_cannot_be_used_with_transparency(self) -> None:
        with patch(
            "sys.argv",
            [
                "pascii",
                "source.png",
                "--save-image",
                "--background",
                "#fff",
                "--transparent",
            ],
        ):
            with redirect_stderr(StringIO()):
                with self.assertRaises(SystemExit) as error:
                    main()

        self.assertEqual(error.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
