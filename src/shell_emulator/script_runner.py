"""Загрузка и выполнение стартовых скриптов эмулятора."""

from dataclasses import dataclass
from pathlib import Path

from .engine import CommandEngine, CommandResult


@dataclass(frozen=True)
class ScriptRun:
    """Результат выполнения стартового скрипта."""

    transcript: list[str]
    failed: bool = False


def read_script(path: Path) -> list[str]:
    """Читает непустые строки скрипта, пропуская строки-комментарии."""
    lines = path.read_text(encoding="utf-8").splitlines()
    return [
        line.strip()
        for line in lines
        if line.strip() and not line.startswith("#")
    ]


def format_result(result: CommandResult) -> list[str]:
    """Преобразует результат команды в строки для интерфейса."""
    lines = []
    if result.output:
        lines.append(result.output)
    if result.error:
        lines.append(f"Ошибка: {result.error}")
    return lines


def run_script(path: Path, engine: CommandEngine) -> ScriptRun:
    """Выполняет скрипт и прекращает работу после первой ошибки."""
    transcript = [f"Стартовый скрипт: {path}"]
    for line in read_script(path):
        transcript.append(f"> {line}")
        result = engine.execute_line(line)
        transcript.extend(format_result(result))
        if not result.ok:
            transcript.append("Скрипт остановлен из-за ошибки.")
            return ScriptRun(transcript=transcript, failed=True)
        if result.should_exit:
            transcript.append("Скрипт завершил работу эмулятора.")
            return ScriptRun(transcript=transcript)
    transcript.append("Стартовый скрипт выполнен успешно.")
    return ScriptRun(transcript=transcript)
