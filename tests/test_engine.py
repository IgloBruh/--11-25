"""Тесты командного ядра без запуска GUI."""

import unittest

from shell_emulator.engine import CommandEngine


class CommandEngineTest(unittest.TestCase):
    """Проверяет требования этапа 1."""

    def setUp(self) -> None:
        self.engine = CommandEngine()

    def test_ls_stub_preserves_quoted_argument(self) -> None:
        result = self.engine.execute_line('ls "folder with spaces"')
        self.assertTrue(result.ok)
        self.assertIn("Команда: ls", result.output)
        self.assertIn("folder with spaces", result.output)

    def test_cd_stub_without_arguments(self) -> None:
        result = self.engine.execute_line("cd")
        self.assertTrue(result.ok)
        self.assertIn("Команда: cd", result.output)

    def test_unknown_command_is_reported(self) -> None:
        result = self.engine.execute_line("pwd")
        self.assertFalse(result.ok)
        self.assertIn("Неизвестная команда", result.error)

    def test_too_many_arguments_are_reported(self) -> None:
        result = self.engine.execute_line("ls one two")
        self.assertFalse(result.ok)
        self.assertIn("Неверное число аргументов", result.error)

    def test_exit_requests_application_shutdown(self) -> None:
        result = self.engine.execute_line("exit")
        self.assertTrue(result.ok)
        self.assertTrue(result.should_exit)

    def test_exit_with_arguments_is_invalid(self) -> None:
        result = self.engine.execute_line("exit now")
        self.assertFalse(result.ok)
        self.assertFalse(result.should_exit)

    def test_empty_line_is_accepted(self) -> None:
        result = self.engine.execute_line("   ")
        self.assertTrue(result.ok)
        self.assertEqual(result.output, "")


if __name__ == "__main__":
    unittest.main()
