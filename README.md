# Эмулятор оболочки ОС

Графический эмулятор командной оболочки для практической работы по
дисциплине «Конфигурационное управление», вариант №9.

Текущая версия включает этапы 1–5:

- графический REPL;
- параметры запуска и стартовые скрипты;
- загрузку виртуальной файловой системы из JSON в память;
- реальные команды `ls` и `cd`;
- команды `cal`, `tree`, `who`, `cp` и `exit`;
- обработку кавычек и ошибок.

## Возможности

- окно `tkinter` с заголовком
  `Эмулятор - [имя_пользователя@имя_компьютера]`;
- разбор аргументов в одинарных и двойных кавычках;
- навигация по VFS с абсолютными и относительными путями;
- отображение файлов и каталогов;
- построение дерева VFS;
- календарь текущего месяца;
- вывод пользователя и имени компьютера;
- копирование файлов и каталогов внутри VFS;
- стартовые скрипты UTF-8 с остановкой при первой ошибке;
- текстовые и бинарные файлы VFS в формате Base64.

Все операции с VFS выполняются в памяти. Исходный JSON-файл не изменяется.

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

Запуск с явными параметрами:

```bat
run.bat ^
  --vfs-path "examples\vfs\files.json" ^
  --script-path "examples\startup\basic.script"
```

Без `run.bat`:

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
| `--vfs-path PATH` | Путь к JSON-файлу VFS | `examples/vfs/minimal.json` |
| `--script-path PATH` | Путь к стартовому скрипту | не задан |

Параметры выводятся в консоль и в окно эмулятора. При ошибке загрузки VFS
показывается сообщение `Ошибка VFS`.

## Команды

### `ls [путь]`

Показывает содержимое каталога. Без аргумента используется текущий каталог.
Каталоги отмечаются символом `/`.

```text
> ls
config.ini docs/ payload.bin

> ls docs
image.bin notes.txt
```

Поддерживаются абсолютные и относительные пути, а также `.` и `..`.

### `cd [путь]`

Переходит в каталог и выводит новый текущий путь. Без аргумента выполняется
переход в корень VFS.

```text
> cd docs
Текущий каталог: /docs

> cd ..
Текущий каталог: /
```

При попытке перейти в несуществующий объект или файл возникает ошибка.

### `tree [путь]`

Показывает дерево указанного каталога. Без аргумента используется текущий
каталог.

```text
> tree
/
├── config.ini
├── docs/
│   ├── image.bin
│   └── notes.txt
└── payload.bin
```

### `cp источник назначение`

Копирует файл или каталог внутри VFS. Копирование выполняется только в памяти:
исходный JSON-файл не изменяется. Каталоги копируются рекурсивно.

```text
> cp readme.txt readme-copy.txt
Скопировано: /readme-copy.txt

> cp docs docs-copy
Скопировано: /docs-copy
```

Источник должен существовать, а путь назначения должен указывать на каталог
или новое имя объекта.

### `cal`

Показывает календарь текущего месяца. Команда не принимает аргументы.

### `who`

Показывает имя пользователя и имя компьютера, на котором запущен эмулятор.
Команда не принимает аргументы.

### `exit`

Завершает работу приложения. Команда не принимает аргументы.

### Обработка ошибок

```text
> ls missing
Ошибка: Путь не найден: /missing

> cd notes.txt
Ошибка: Не каталог: notes.txt

> cp missing.txt copy.txt
Ошибка: Путь не найден: /missing.txt

> cal now
Ошибка: Неверное число аргументов для cal: ожидался максимум 0

> unknown-command
Ошибка: Неизвестная команда: unknown-command
```

## Формат VFS

VFS хранится в JSON-файле. Корневой объект должен быть каталогом:

```json
{
  "name": "/",
  "type": "directory",
  "children": [
    {
      "name": "docs",
      "type": "directory",
      "children": [
        {
          "name": "notes.txt",
          "type": "file",
          "data": "Текстовый файл\n"
        }
      ]
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
По умолчанию данные кодируются как UTF-8. Для бинарных данных используется
`"encoding": "base64"`.

В проекте есть три VFS:

- `examples/vfs/minimal.json` — корень и один файл;
- `examples/vfs/files.json` — несколько файлов, каталог и бинарный файл;
- `examples/vfs/deep.json` — дерево с глубиной не менее трёх уровней.

## Стартовые скрипты

Стартовый скрипт — UTF-8-файл с одной командой на строку. Пустые строки и
строки, начинающиеся с `#`, пропускаются. Команды и результаты отображаются
в окне. После первой ошибки выполнение прекращается.

Пример `examples/startup/basic.script`:

```text
ls
cd .
cp readme.txt readme-copy.txt
tree
cal
who
exit
```

Демонстрационные Windows-сценарии:

```bat
examples\windows\run-minimal.bat
examples\windows\run-files.bat
examples\windows\run-deep.bat
```

Они проверяют параметры запуска и разные варианты VFS.

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

Тесты проверяют парсер, команды REPL, навигацию по VFS, копирование файлов и
каталогов, дерево, календарь, обработку ошибок, параметры запуска и стартовые
скрипты.

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
