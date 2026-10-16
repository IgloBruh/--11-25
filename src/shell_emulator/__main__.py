"""Точка входа для запуска пакета как модуля."""

from .config import debug_lines, parse_config
from .gui import main


if __name__ == "__main__":
    configuration = parse_config()
    for line in debug_lines(configuration):
        print(line)
    main(configuration)
