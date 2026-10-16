"""Загрузка виртуальной файловой системы из JSON в память."""

import base64
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass
class VfsNode:
    """Узел виртуальной файловой системы."""

    name: str
    kind: str
    data: bytes = b""
    children: Dict[str, "VfsNode"] = field(default_factory=dict)


class VfsError(ValueError):
    """Ошибка структуры или содержимого VFS."""


class VirtualFileSystem:
    """Иммутабельно используемая в эмуляторе VFS, загруженная в память."""

    def __init__(self, root: VfsNode, source: Path) -> None:
        self.root = root
        self.source = source

    @classmethod
    def from_file(cls, path: Path) -> "VirtualFileSystem":
        """Загружает VFS из JSON-файла и проверяет его структуру."""
        try:
            document = json.loads(path.read_text(encoding="utf-8"))
        except OSError as error:
            raise VfsError(f"Не удалось прочитать VFS: {error}") from error
        except json.JSONDecodeError as error:
            raise VfsError(f"Некорректный JSON VFS: {error}") from error
        root = cls._parse_node(document, expected_kind="directory")
        return cls(root, path)

    @classmethod
    def _parse_node(
        cls,
        raw_node: Any,
        expected_kind: Optional[str] = None,
    ) -> VfsNode:
        """Проверяет JSON-узел и превращает его в объект VFS."""
        if not isinstance(raw_node, dict):
            raise VfsError("Узел VFS должен быть JSON-объектом")
        name = raw_node.get("name")
        kind = raw_node.get("type")
        if not isinstance(name, str) or not name:
            raise VfsError("Узел VFS должен иметь непустое имя")
        if kind not in {"file", "directory"}:
            raise VfsError(f"Неизвестный тип узла: {kind}")
        if expected_kind and kind != expected_kind:
            raise VfsError("Корневой узел VFS должен быть каталогом")
        if kind == "file":
            return VfsNode(name=name, kind=kind, data=cls._file_data(raw_node))
        return cls._directory_node(name, raw_node)

    @classmethod
    def _directory_node(cls, name: str, raw_node: Dict[str, Any]) -> VfsNode:
        """Создаёт каталог и проверяет имена его дочерних узлов."""
        raw_children = raw_node.get("children", [])
        if not isinstance(raw_children, list):
            raise VfsError(f"Дети каталога {name} должны быть массивом")
        node = VfsNode(name=name, kind="directory")
        for raw_child in raw_children:
            child = cls._parse_node(raw_child)
            if child.name in node.children:
                raise VfsError(f"Дублирующееся имя в каталоге {name}")
            node.children[child.name] = child
        return node

    @staticmethod
    def _file_data(raw_node: Dict[str, Any]) -> bytes:
        """Декодирует текстовые или base64-данные файла."""
        data = raw_node.get("data", "")
        encoding = raw_node.get("encoding", "utf-8")
        if not isinstance(data, str):
            raise VfsError("Данные файла должны быть строкой")
        if encoding == "utf-8":
            return data.encode("utf-8")
        if encoding == "base64":
            try:
                return base64.b64decode(data, validate=True)
            except ValueError as error:
                raise VfsError("Некорректные base64-данные файла") from error
        raise VfsError(f"Неизвестная кодировка файла: {encoding}")

    def count_nodes(self) -> int:
        """Возвращает количество узлов в загруженной VFS."""
        return self._count(self.root)

    @staticmethod
    def _count(node: VfsNode) -> int:
        """Рекурсивно считает узлы дерева."""
        children_count = sum(
            VirtualFileSystem._count(child)
            for child in node.children.values()
        )
        return 1 + children_count

    def read_file(self, name: str) -> bytes:
        """Возвращает байты файла из корня VFS для проверки данных."""
        node = self.root.children.get(name)
        if node is None or node.kind != "file":
            raise VfsError(f"Файл не найден в корне VFS: {name}")
        return node.data
