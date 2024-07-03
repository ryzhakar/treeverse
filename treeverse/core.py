"""Treeverse library for file tree traversal and manipulation."""
from __future__ import annotations

from collections.abc import Callable
from collections.abc import Sequence
from datetime import datetime
from pathlib import Path
from typing import Any

import chardet

from treeverse.models import FileInfo
from treeverse.models import FileNode


def traverse_tree(
    path: Path | str,
    depth_limit: int | None = None,
    filter_funcs: Sequence[Callable[[FileNode], bool]] = (),
    text_files_only: bool = True,
) -> FileNode | None:
    """Traverses the file tree recursively."""
    initial_tree = _build_tree(
        Path(path),
        current_depth=0,
        depth_limit=depth_limit,
    )
    if not initial_tree:
        return None

    return _apply_filters(
        initial_tree,
        filter_funcs=filter_funcs,
        text_files_only=text_files_only,
    )


def process_tree(
    tree: FileNode,
    payload_func: Callable[[FileNode], dict[str, Any]],
) -> FileNode:
    """Process the tree and add custom data to nodes."""
    def _process_node(node: FileNode) -> FileNode:
        processed_node = node.model_copy(
            update={'custom_data': payload_func(node)},
        )
        processed_node = processed_node.model_copy(
            update={
                'child_nodes': [
                    _process_node(child) for child in node.child_nodes
                ],
            },
        )
        return processed_node

    return _process_node(tree)


def reduce_tree(
    tree: FileNode,
    reduction_func: Callable[[FileNode], dict[str, Any]],
) -> FileNode:
    """Reduces the file tree recursively.

    Reduction function should return model update data.
    """
    def reduce(node: FileNode) -> FileNode:
        node.child_nodes = [
            reduce(child) for child in node.child_nodes
        ]
        node = node.model_copy(
            update=reduction_func(node),
        )
        return node

    return reduce(tree)


def _apply_filters(
    node: FileNode,
    *,
    filter_funcs: Sequence[Callable[[FileNode], bool]],
    text_files_only: bool = True,
) -> FileNode | None:
    is_dir = node.file_info.full_path.is_dir()
    if not is_dir:
        nontext_file = not node.file_info.is_text_file
        if text_files_only and nontext_file:
            return None
        if all(filter_func(node) for filter_func in filter_funcs):
            return node
        return None

    filtered_children = list(
        filter(
            None,
            (
                _apply_filters(
                    child,
                    filter_funcs=filter_funcs,
                    text_files_only=text_files_only,
                )
                for child in node.child_nodes
            ),
        ),
    )

    if not filtered_children:
        return None

    return node.model_copy(update={'child_nodes': filtered_children})


# TODO: simplify, split up
def _build_tree(  # noqa: WPS210
    current_path: Path,
    *,
    current_depth: int,
    depth_limit: int | None = None,
) -> FileNode | None:
    if depth_limit is not None and current_depth > depth_limit:
        return None

    is_file = current_path.is_file()
    is_dir = current_path.is_dir()
    is_text = _is_text_file(current_path) if is_file else False

    file_stat = current_path.stat()
    textual_info = _get_text_file_info(current_path) if is_text else {}
    file_info = FileInfo(
        full_path=current_path,
        file_size_bytes=file_stat.st_size,
        last_modified=datetime.fromtimestamp(file_stat.st_mtime),
        is_text_file=is_text,
        **textual_info,
    )

    node = FileNode(
        file_name=current_path.name,
        file_info=file_info,
    )

    if not is_dir:
        return node

    for child_path in current_path.iterdir():
        child_node = _build_tree(
            child_path,
            current_depth=current_depth + 1,
            depth_limit=depth_limit,
        )
        if child_node:
            node = node.add_child(child_node)
    return node


def _is_text_file(file_path: Path) -> bool:
    """Check if a file is likely to be a text file."""
    with file_path.open('r', encoding='utf-8') as potential_text:
        try:
            return bool(potential_text.read())
        except UnicodeDecodeError:
            return False


def _get_text_file_info(file_path: Path) -> dict[str, Any]:
    """Get text file information."""
    with file_path.open('rb') as txfile:
        byte_text = txfile.read()
        detected_encoding = chardet.detect(byte_text)['encoding'] or 'utf-8'
        text = byte_text.decode(detected_encoding)

    return {
        'text_encoding': detected_encoding,
        'line_count': text.count('\n') + 1,
        'word_count': len(text.split()),
        'character_count': len(text),
    }
