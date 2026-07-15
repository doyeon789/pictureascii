from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from PIL import Image

from pictureascii.cli import convert_image_to_ascii


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


if __name__ == "__main__":
    unittest.main()
