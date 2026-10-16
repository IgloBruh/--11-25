"""Графический интерфейс эмулятора командной оболочки."""

import getpass
import socket
import tkinter as tk
from tkinter import scrolledtext

from .engine import CommandEngine


class ShellWindow:
    """Окно REPL с полем вывода и строкой ввода."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.engine = CommandEngine()
        username = getpass.getuser()
        hostname = socket.gethostname()
        self.root.title(f"Эмулятор - [{username}@{hostname}]")
        self.root.geometry("720x480")
        self._build_widgets()
        self._write("Эмулятор оболочки. Доступны команды: ls, cd, exit.")
        self._write_prompt()

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
        if result.output:
            self._write(result.output)
        if result.error:
            self._write(f"Ошибка: {result.error}")
        if result.should_exit:
            self.root.destroy()
        else:
            self._write_prompt()
        return "break"


def main() -> None:
    """Запускает приложение."""
    root = tk.Tk()
    ShellWindow(root)
    root.mainloop()
