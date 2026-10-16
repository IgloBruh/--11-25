# Эмулятор оболочки ОС

Графический эмулятор командной оболочки для практической работы по
дисциплине «Конфигурационное управление», вариант №9.

Текущая версия включает этапы 1–3:

- графический REPL;
- команды `ls`, `cd` и `exit`;
- обработку кавычек и ошибок;
- параметры запуска;
- стартовые скрипты;
- загрузку виртуальной файловой системы из JSON в память;
- поддержку текстовых и бинарных файлов в формате Base64.

## Возможности

- окно `tkinter` с заголовком
  `Эмулятор - [имя_пользователя@имя_компьютера]`;
- разбор аргументов в одинарных и двойных кавычках;
- сообщения об неизвестных командах и неверных аргументах;
- стартовые скрипты UTF-8 с остановкой при первой ошибке;
- пропуск пустых строк и строк-комментариев в стартовых скриптах;
- чтение VFS из JSON без изменения исходного файла;
- хранение загруженной VFS в оперативной памяти;
- проверка структуры VFS и декодирование Base64-данных.

На текущем этапе `ls` и `cd` являются командами-заглушками: они выводят имя
команды и переданные аргументы, но ещё не изменяют и не отображают VFS.

## Требования

- Windows 10/11 или Linux/macOS;
- Python 3.9 или новее;
- `tkinter`;
- графическая среда рабочего стола.

Внешние Python-зависимости не используются.

Для Windows установите Python с включённым компонентом **Tcl/Tk and IDLE**.
Скачать Python можно на <https://www.python.org/downloads/>.

## Запуск в Windows

Из корня проекта:

```bat
run.bat
```

По умолчанию загружается файл `examples/vfs/minimal.json`.

Запуск с явными параметрами:

```bat
run.bat ^
  --vfs-path "examples\vfs\files.json" ^
  --script-path "examples\startup\basic.script"
```

Доступен запуск без `run.bat`:

```bat
set PYTHONPATH=src
py -3 -m shell_emulator ^
  --vfs-path "examples\vfs\files.json" ^
  --script-path "examples\startup\basic.script"
```

В PowerShell:

```powershell
$env:PYTHONPATH = "src"
py -3 -m shell_emulator `
  --vfs-path "examples/vfs/files.json" `
  --script-path "examples/startup/basic.script"
```

## Запуск в Linux/macOS

```bash
PYTHONPATH=src python3 -m shell_emulator \
  --vfs-path examples/vfs/files.json \
  --script-path examples/startup/basic.script
```

## Параметры запуска

| Параметр | Описание | По умолчанию |
|---|---|---|
| `--vfs-path PATH` | Путь к JSON-файлу виртуальной файловой системы | `examples/vfs/minimal.json` |
| `--script-path PATH` | Путь к стартовому скрипту | не задан |

При запуске параметры выводятся в консоль и в окно эмулятора.

## Команды REPL

### `ls [аргумент]`

Команда-заглушка. Выводит имя команды и аргумент. Допускается не более одного
аргумента.

```text
> ls "folder with spaces"
Команда: ls
Аргументы: folder with spaces
```

### `cd [аргумент]`

Команда-заглушка с таким же форматом вывода:

```text
> cd /tmp
Команда: cd
Аргументы: /tmp
```

### `exit`

Завершает работу приложения:

```text
> exit
Завершение работы.
```

### Ошибки

```text
> pwd
Ошибка: Неизвестная команда: pwd

> ls one two
Ошибка: Неверное число аргументов для ls: ожидался максимум 1
```

## Формат VFS

VFS хранится в JSON-файле. Корневой объект должен быть каталогом:

```json
{
  "name": "/",
  "type": "directory",
  "children": [
    {
      "name": "readme.txt",
      "type": "file",
      "data": "Текстовый файл\n"
    },
    {
      "name": "payload.bin",
      "type": "file",
      "encoding": "base64",
      "data": "AAECAwQF"
    }
  ]
}
```

Узел каталога содержит `children`. Узел файла содержит строковое поле `data`.
По умолчанию `data` кодируется как UTF-8. Для бинарных данных указывается
`"encoding": "base64"`.

В проекте есть три варианта VFS:

- `examples/vfs/minimal.json` — корень и один файл;
- `examples/vfs/files.json` — несколько файлов, каталог и Base64-файл;
- `examples/vfs/deep.json` — дерево с глубиной не менее трёх уровней.

При ошибке чтения, JSON или структуры VFS приложение показывает сообщение
`Ошибка VFS`.

## Стартовые скрипты

Стартовый скрипт — текстовый файл UTF-8, одна команда на строку. Пустые строки
и строки, начинающиеся с `#`, пропускаются.

Пример `examples/startup/basic.script`:

```text
ls "folder with spaces"
cd /tmp
exit
```

При выполнении скрипта в окне отображаются ввод и вывод. После первой ошибки
скрипт прекращается:

```text
> unknown-command
Ошибка: Неизвестная команда: unknown-command
Скрипт остановлен из-за ошибки.
```

## Демонстрационные сценарии Windows

В каталоге `examples/windows` находятся сценарии для проверки разных VFS:

```bat
examples\windows\run-minimal.bat
examples\windows\run-files.bat
examples\windows\run-deep.bat
```

Каждый сценарий запускает эмулятор с параметрами `--vfs-path` и
`--script-path`.

## Структура проекта

```text
.
├── README.md
├── .gitignore
├── run.bat
├── run.sh
├── examples
│   ├── startup
│   │   ├── basic.script
│   │   └── error.script
│   ├── vfs
│   │   ├── deep.json
│   │   ├── files.json
│   │   └── minimal.json
│   └── windows
│       ├── run-deep.bat
│       ├── run-files.bat
│       └── run-minimal.bat
├── src
│   └── shell_emulator
│       ├── config.py
│       ├── engine.py
│       ├── gui.py
│       ├── script_runner.py
│       ├── vfs.py
│       └── __main__.py
└── tests
    ├── test_engine.py
    ├── test_stage2.py
    └── test_vfs.py
```

## Тестирование

Windows CMD:

```bat
set PYTHONPATH=src
py -3 -m unittest discover -s tests -v
```

PowerShell:

```powershell
$env:PYTHONPATH = "src"
py -3 -m unittest discover -s tests -v
```

Linux/macOS:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

Тесты проверяют команды REPL, параметры запуска, стартовые скрипты, загрузку
JSON, структуру каталогов, текстовые данные и Base64-файлы.
