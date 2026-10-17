"""Тесты командного ядра четвёртого этапа."""

from pathlib import Path
import unittest

from shell_emulator.engine import CommandEngine
from shell_emulator.vfs import VirtualFileSystem


VFS_PATH = Path(__file__).parents[1] / "examples" / "vfs" / "files.json"


class CommandEngineTest(unittest.TestCase):
    """Проверяет команды REPL и операции с VFS."""

    def test_ls_lists_root_entries(self) -> None:
        self.engine = CommandEngine(VirtualFileSystem.from_file(VFS_PATH))
        result = self.engine.execute_line("ls")
        self.assertTrue(result.ok)
        self.assertIn("config.ini", result.output)
        self.assertIn("docs/", result.output)

    def test_ls_supports_quoted_directory_path(self) -> None:
        self.engine = CommandEngine(VirtualFileSystem.from_file(VFS_PATH))
        result = self.engine.execute_line('ls "docs"')
        self.assertTrue(result.ok)
        self.assertIn("image.bin", result.output)
        self.assertIn("notes.txt", result.output)

    def test_cd_changes_current_directory(self) -> None:
        self.engine = CommandEngine(VirtualFileSystem.from_file(VFS_PATH))
        result = self.engine.execute_line("cd docs")
        self.assertTrue(result.ok)
        self.assertIn("/docs", result.output)
        listing = self.engine.execute_line("ls")
        self.assertIn("notes.txt", listing.output)

    def test_cd_supports_parent_directory(self) -> None:
        self.engine = CommandEngine(VirtualFileSystem.from_file(VFS_PATH))
        self.engine.execute_line("cd docs")
        result = self.engine.execute_line("cd ..")
        self.assertTrue(result.ok)
        self.assertIn("/", result.output)

    def test_tree_prints_nested_vfs(self) -> None:
        self.engine = CommandEngine(VirtualFileSystem.from_file(VFS_PATH))
        result = self.engine.execute_line("tree")
        self.assertTrue(result.ok)
        self.assertIn("docs/", result.output)
        self.assertIn("notes.txt", result.output)

    def test_cp_copies_file_only_in_memory(self) -> None:
        self.engine = CommandEngine(VirtualFileSystem.from_file(VFS_PATH))
        result = self.engine.execute_line("cp readme.txt copy.txt")
        self.assertTrue(result.ok)
        listing = self.engine.execute_line("ls")
        self.assertIn("copy.txt", listing.output)

    def test_cp_copies_directory_recursively(self) -> None:
        self.engine = CommandEngine(VirtualFileSystem.from_file(VFS_PATH))
        result = self.engine.execute_line("cp docs docs-copy")
        self.assertTrue(result.ok)
        listing = self.engine.execute_line("ls docs-copy")
        self.assertIn("notes.txt", listing.output)

    def test_cp_reports_missing_source(self) -> None:
        self.engine = CommandEngine(VirtualFileSystem.from_file(VFS_PATH))
        result = self.engine.execute_line("cp missing.txt copy.txt")
        self.assertFalse(result.ok)
        self.assertIn("Путь не найден", result.error)

    def test_cp_requires_source_and_destination(self) -> None:
        self.engine = CommandEngine(VirtualFileSystem.from_file(VFS_PATH))
        result = self.engine.execute_line("cp readme.txt")
        self.assertFalse(result.ok)
        self.assertIn("cp ожидает источник", result.error)

    def test_invalid_vfs_path_is_reported(self) -> None:
        self.engine = CommandEngine(VirtualFileSystem.from_file(VFS_PATH))
        result = self.engine.execute_line("cd missing")
        self.assertFalse(result.ok)
        self.assertIn("Путь не найден", result.error)

    def test_new_commands_are_available(self) -> None:
        self.engine = CommandEngine(VirtualFileSystem.from_file(VFS_PATH))
        self.assertTrue(self.engine.execute_line("cal").ok)
        self.assertTrue(self.engine.execute_line("who").ok)

    def test_command_argument_errors_are_reported(self) -> None:
        self.engine = CommandEngine(VirtualFileSystem.from_file(VFS_PATH))
        result = self.engine.execute_line("cal now")
        self.assertFalse(result.ok)
        self.assertIn("Неверное число аргументов", result.error)

    def test_unknown_command_is_reported(self) -> None:
        self.engine = CommandEngine(VirtualFileSystem.from_file(VFS_PATH))
        result = self.engine.execute_line("pwd")
        self.assertFalse(result.ok)
        self.assertIn("Неизвестная команда", result.error)

    def test_exit_requests_application_shutdown(self) -> None:
        self.engine = CommandEngine(VirtualFileSystem.from_file(VFS_PATH))
        result = self.engine.execute_line("exit")
        self.assertTrue(result.ok)
        self.assertTrue(result.should_exit)

    def test_empty_line_is_accepted(self) -> None:
        self.engine = CommandEngine(VirtualFileSystem.from_file(VFS_PATH))
        result = self.engine.execute_line("   ")
        self.assertTrue(result.ok)
        self.assertEqual(result.output, "")


if __name__ == "__main__":
    unittest.main()
