import tempfile
import unittest
from pathlib import Path

from path_safety import unique_destination


class OutputSafetyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "source.jpg"
        self.source.write_bytes(b"original")

    def test_free_destination_is_preserved(self):
        output = self.root / "output"
        output.mkdir()
        desired = output / "photo.jpg"
        self.assertEqual(
            unique_destination(desired, self.source, allow_original=False),
            desired,
        )

    def test_existing_destination_is_preserved(self):
        output = self.root / "output"
        output.mkdir()
        desired = output / "photo.jpg"
        desired.write_bytes(b"previous")

        result = unique_destination(
            desired, self.source, allow_original=False
        )

        self.assertEqual(result, output / "photo_1.jpg")
        self.assertEqual(desired.read_bytes(), b"previous")

    def test_multiple_collisions_are_skipped(self):
        output = self.root / "output"
        output.mkdir()
        (output / "photo.jpg").write_bytes(b"one")
        (output / "photo_1.jpg").write_bytes(b"two")

        result = unique_destination(
            output / "photo.jpg", self.source, allow_original=False
        )

        self.assertEqual(result, output / "photo_2.jpg")

    def test_original_path_requires_explicit_permission(self):
        self.assertEqual(
            unique_destination(self.source, self.source),
            self.root / "source_1.jpg",
        )
        self.assertEqual(
            unique_destination(
                self.source, self.source, allow_original=True
            ),
            self.source,
        )

    def test_broken_symlink_is_a_collision(self):
        output = self.root / "output"
        output.mkdir()
        desired = output / "photo.jpg"

        try:
            desired.symlink_to(output / "missing.jpg")
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"Symbolic links unavailable: {exc}")

        result = unique_destination(
            desired, self.source, allow_original=False
        )

        self.assertEqual(result, output / "photo_1.jpg")
        self.assertTrue(desired.is_symlink())


if __name__ == "__main__":
    unittest.main()
