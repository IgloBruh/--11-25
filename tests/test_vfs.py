"""Тесты виртуальной файловой системы третьего этапа."""

from pathlib import Path
import unittest

from shell_emulator.vfs import VirtualFileSystem, VfsError


VFS_DIRECTORY = Path(__file__).parents[1] / "examples" / "vfs"


class VirtualFileSystemTest(unittest.TestCase):
    """Проверяет загрузку всех демонстрационных вариантов VFS."""

    def test_minimal_vfs_is_loaded_in_memory(self) -> None:
        vfs = VirtualFileSystem.from_file(VFS_DIRECTORY / "minimal.json")
        self.assertEqual(vfs.count_nodes(), 2)
        self.assertEqual(vfs.read_file("readme.txt"), b"Minimal VFS\n")

    def test_text_and_base64_files_are_supported(self) -> None:
        vfs = VirtualFileSystem.from_file(VFS_DIRECTORY / "files.json")
        self.assertEqual(vfs.count_nodes(), 6)
        self.assertEqual(vfs.read_file("config.ini"), b"[app]\nname=emulator\n")
        self.assertEqual(
            vfs.read_file("payload.bin"), b"\x00\x01\x02\x03\x04\x05"
        )

    def test_deep_vfs_contains_three_directory_levels(self) -> None:
        vfs = VirtualFileSystem.from_file(VFS_DIRECTORY / "deep.json")
        self.assertEqual(vfs.count_nodes(), 5)

    def test_invalid_json_is_reported(self) -> None:
        with self.assertRaises(VfsError):
            VirtualFileSystem.from_file(VFS_DIRECTORY / "missing.json")


if __name__ == "__main__":
    unittest.main()
