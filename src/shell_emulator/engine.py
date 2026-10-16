"""Ядро обработки команд эмулятора оболочки."""

from dataclasses import dataclass
import shlex
from typing import Callable, Dict, List, Optional


MAX_ARGUMENTS = 1


@dataclass(frozen=True)
class CommandResult:
    """Результат выполнения одной команды."""

    output: str = ""
    error: Optional[str] = None
    should_exit: bool = False

    @property
    def ok(self) -> bool:
        """Возвращает признак успешного выполнения команды."""
        return self.error is None


class CommandEngine:

    def __init__(self) -> None:
        self._commands: Dict[str, Callable[[List[str]], CommandResult]] = {
            "ls": self._stub_command,
            "cd": self._stub_command,
            "exit": self._exit_command,
        }

    def execute_line(self, line: str) -> CommandResult:
        """Разбирает и выполняет строку, введённую пользователем."""
        try:
            tokens = shlex.split(line)
        except ValueError as error:
            return CommandResult(error=f"Ошибка разбора: {error}")

        if not tokens:
            return CommandResult()

        command, arguments = tokens[0], tokens[1:]
        handler = self._commands.get(command)
        if handler is None:
            return CommandResult(error=f"Неизвестная команда: {command}")
        return handler([command, *arguments])

    def _stub_command(self, tokens: List[str]) -> CommandResult:
        """Возвращает имя команды и переданные ей аргументы."""
        if len(tokens) - 1 > MAX_ARGUMENTS:
            return CommandResult(
                error=(
                    f"Неверное число аргументов для {tokens[0]}: "
                    f"ожидался максимум {MAX_ARGUMENTS}"
                )
            )
        arguments = " ".join(tokens[1:])
        output = f"Команда: {tokens[0]}\nАргументы: {arguments}"
        return CommandResult(output=output)

    def _exit_command(self, tokens: List[str]) -> CommandResult:
        """Завершает работу эмулятора при отсутствии аргументов."""
        if len(tokens) != 1:
            return CommandResult(
                error="Неверные аргументы: exit не принимает аргументы"
            )
        return CommandResult(output="Завершение работы.", should_exit=True)
