"""Ядро команд эмулятора оболочки."""

import calendar
from dataclasses import dataclass
from datetime import datetime
import getpass
import shlex
import socket
from typing import Callable, Dict, List, Optional

from .vfs import PathParts, VirtualFileSystem, VfsError


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
    """Разбирает строки и выполняет команды текущего этапа."""

    def __init__(self, vfs: Optional[VirtualFileSystem] = None) -> None:
        self.vfs = vfs
        self.current_path: PathParts = ()
        self._commands: Dict[str, Callable[[List[str]], CommandResult]] = {
            "ls": self._list_command,
            "cd": self._change_directory_command,
            "cal": self._calendar_command,
            "tree": self._tree_command,
            "who": self._who_command,
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
        handler = self._commands.get(tokens[0])
        if handler is None:
            return CommandResult(error=f"Неизвестная команда: {tokens[0]}")
        return handler(tokens)

    def _validate_arguments(
        self,
        tokens: List[str],
        maximum: int,
    ) -> Optional[CommandResult]:
        """Проверяет максимальное число аргументов команды."""
        if len(tokens) - 1 > maximum:
            return CommandResult(
                error=(
                    f"Неверное число аргументов для {tokens[0]}: "
                    f"ожидался максимум {maximum}"
                )
            )
        return None

    def _require_vfs(self) -> Optional[CommandResult]:
        """Возвращает ошибку, если VFS не была загружена."""
        if self.vfs is None:
            return CommandResult(error="VFS не загружена")
        return None

    def _list_command(self, tokens: List[str]) -> CommandResult:
        """Показывает содержимое каталога VFS."""
        invalid = self._validate_arguments(tokens, 1)
        missing_vfs = self._require_vfs()
        if invalid or missing_vfs:
            return invalid or missing_vfs  # type: ignore[return-value]
        try:
            path = tokens[1] if len(tokens) == 2 else "."
            target = self.vfs.resolve(path, self.current_path)
            nodes = self.vfs.list_directory(target)
        except VfsError as error:
            return CommandResult(error=str(error))
        names = [node.name + ("/" if node.kind == "directory" else "")
                 for node in nodes]
        return CommandResult(output=" ".join(names) or "(пусто)")

    def _change_directory_command(self, tokens: List[str]) -> CommandResult:
        """Изменяет текущий каталог VFS."""
        invalid = self._validate_arguments(tokens, 1)
        missing_vfs = self._require_vfs()
        if invalid or missing_vfs:
            return invalid or missing_vfs  # type: ignore[return-value]
        try:
            path = tokens[1] if len(tokens) == 2 else "/"
            self.current_path = self.vfs.change_directory(
                path, self.current_path
            )
        except VfsError as error:
            return CommandResult(error=str(error))
        current = self.vfs.current_name(self.current_path)
        return CommandResult(output=f"Текущий каталог: {current}")

    def _tree_command(self, tokens: List[str]) -> CommandResult:
        """Показывает дерево VFS начиная с текущего каталога."""
        invalid = self._validate_arguments(tokens, 1)
        missing_vfs = self._require_vfs()
        if invalid or missing_vfs:
            return invalid or missing_vfs  # type: ignore[return-value]
        try:
            path = tokens[1] if len(tokens) == 2 else "."
            target = self.vfs.resolve(path, self.current_path)
            return CommandResult(output=self.vfs.tree(target))
        except VfsError as error:
            return CommandResult(error=str(error))

    def _calendar_command(self, tokens: List[str]) -> CommandResult:
        """Показывает календарь текущего месяца."""
        invalid = self._validate_arguments(tokens, 0)
        if invalid:
            return invalid
        now = datetime.now()
        output = calendar.TextCalendar().formatmonth(now.year, now.month)
        return CommandResult(output=output.rstrip())

    def _who_command(self, tokens: List[str]) -> CommandResult:
        """Показывает пользователя и имя текущего компьютера."""
        invalid = self._validate_arguments(tokens, 0)
        if invalid:
            return invalid
        user = getpass.getuser()
        host = socket.gethostname()
        return CommandResult(output=f"{user} {host}")

    def _exit_command(self, tokens: List[str]) -> CommandResult:
        """Завершает работу эмулятора при отсутствии аргументов."""
        invalid = self._validate_arguments(tokens, 0)
        if invalid:
            return invalid
        return CommandResult(output="Завершение работы.", should_exit=True)
