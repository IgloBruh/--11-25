"""Тесты конфигурации и стартовых скриптов второго этапа."""

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from shell_emulator.config import debug_lines, parse_config
from shell_emulator.engine import CommandEngine
from shell_emulator.script_runner import run_script


class StageTwoTest(unittest.TestCase):
    """Проверяет требования этапа 2."""

    def test_command_line_parameters_are_parsed(self) -> None:
        config = parse_config(
            ["--vfs-path", "data", "--script-path", "start.script"]
        )
        self.assertEqual(config.vfs_path, Path("data"))
        self.assertEqual(config.script_path, Path("start.script"))
        lines = debug_lines(config)
        self.assertIn("  VFS: data", lines)
        self.assertIn("  Стартовый скрипт: start.script", lines)

    def test_default_parameters_are_available(self) -> None:
        config = parse_config([])
        self.assertEqual(config.vfs_path, Path("examples/vfs/minimal.json"))
        self.assertIsNone(config.script_path)

    def test_script_stops_after_first_error(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "start.script"
            path.write_text(
                "ls first\nunknown\nls never-reached\n",
                encoding="utf-8",
            )
            result = run_script(path, CommandEngine())

        self.assertTrue(result.failed)
        transcript = "\n".join(result.transcript)
        self.assertIn("> ls first", transcript)
        self.assertIn("> unknown", transcript)
        self.assertNotIn("never-reached", transcript)
        self.assertIn("Скрипт остановлен из-за ошибки.", transcript)

    def test_comments_and_empty_lines_are_ignored(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "start.script"
            path.write_text("# comment\n\ncd /tmp\n", encoding="utf-8")
            result = run_script(path, CommandEngine())

        self.assertFalse(result.failed)
        self.assertIn("> cd /tmp", result.transcript)


if __name__ == "__main__":
    unittest.main()
