"""Разбор параметров запуска эмулятора."""

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Sequence


@dataclass(frozen=True)
class AppConfig:
    """Параметры запуска приложения."""

    vfs_path: Path
    script_path: Optional[Path]


def build_parser() -> argparse.ArgumentParser:
    """Создаёт парсер аргументов командной строки."""
    parser = argparse.ArgumentParser(
        description="Графический эмулятор оболочки, вариант 9."
    )
    parser.add_argument(
        "--vfs-path",
        type=Path,
        default=Path("."),
        help="Путь к физическому расположению VFS.",
    )
    parser.add_argument(
        "--script-path",
        type=Path,
        default=None,
        help="Путь к стартовому скрипту эмулятора.",
    )
    return parser


def parse_config(arguments: Optional[Sequence[str]] = None) -> AppConfig:
    """Преобразует аргументы командной строки в конфигурацию."""
    parsed = build_parser().parse_args(arguments)
    return AppConfig(
        vfs_path=parsed.vfs_path,
        script_path=parsed.script_path,
    )


def debug_lines(config: AppConfig) -> list[str]:
    """Формирует отладочные строки со всеми параметрами запуска."""
    script = str(config.script_path) if config.script_path else "не задан"
    return [
        "Параметры запуска:",
        f"  VFS: {config.vfs_path}",
        f"  Стартовый скрипт: {script}",
    ]
