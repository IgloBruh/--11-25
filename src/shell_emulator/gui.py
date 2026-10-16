"""Графический интерфейс эмулятора командной оболочки."""

import getpass
import socket
import tkinter as tk
from pathlib import Path
from tkinter import scrolledtext
from typing import Iterable, Optional

from .config import AppConfig, debug_lines
from .engine import CommandEngine
from .script_runner import run_script


class ShellWindow:
    """Окно REPL с полем вывода и строкой ввода."""

    def __init__(self, root: tk.Tk, config: AppConfig) -> None:
        self.root = root
        self.engine = CommandEngine()
        self.config = config
        self._configure_window()
        self._build_widgets()
        self._show_startup()

    def _configure_window(self) -> None:
        """Настраивает заголовок и размер окна."""
        username = getpass.getuser()
        hostname = socket.gethostname()
        self.root.title(f"Эмулятор - [{username}@{hostname}]")
        self.root.geometry("720x480")

    def _build_widgets(self) -> None:
        """Создаёт элементы графического интерфейса."""
        self.output = scrolledtext.ScrolledText(
            self.root,
            state="disabled",
            wrap=tk.WORD,
            font=("Courier New", 11),
        )
        self.output.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        self.entry = tk.Entry(self.root, font=("Courier New", 11))
        self.entry.pack(fill=tk.X, padx=8, pady=(0, 8))
        self.entry.bind("<Return>", self._submit)
        self.entry.focus_set()

    def _show_startup(self) -> None:
        """Показывает параметры и выполняет заданный стартовый скрипт."""
        self._write_lines(debug_lines(self.config))
        self._write("Эмулятор оболочки. Доступны команды: ls, cd, exit.")
        if self.config.script_path:
            self._run_startup_script(self.config.script_path)
        self._write_prompt()

    def _run_startup_script(self, path: Path) -> None:
        """Показывает результат выполнения стартового скрипта."""
        try:
            result = run_script(path, self.engine)
        except OSError as error:
            self._write(f"Ошибка чтения стартового скрипта: {error}")
            return
        self._write_lines(result.transcript)

    def _write_lines(self, lines: Iterable[str]) -> None:
        """Добавляет несколько строк в область вывода."""
        for line in lines:
            self._write(line)

    def _write(self, text: str) -> None:
        """Добавляет текст в область вывода."""
        self.output.configure(state="normal")
        self.output.insert(tk.END, f"{text}\n")
        self.output.configure(state="disabled")
        self.output.see(tk.END)

    def _write_prompt(self) -> None:
        """Показывает приглашение к вводу."""
        self._write("> ")

    def _submit(self, _event: tk.Event) -> str:
        """Передаёт введённую строку ядру и показывает результат."""
        line = self.entry.get()
        self.entry.delete(0, tk.END)
        self._write(f"> {line}")
        result = self.engine.execute_line(line)
        self._write_lines([result.output] if result.output else [])
        self._write_lines([f"Ошибка: {result.error}"] if result.error else [])
        if result.should_exit:
            self.root.destroy()
        else:
            self._write_prompt()
        return "break"


def main(config: Optional[AppConfig] = None) -> None:
    """Запускает приложение с заданной конфигурацией."""
    active_config = config or AppConfig(Path("."), None)
    root = tk.Tk()
    ShellWindow(root, active_config)
    root.mainloop()
