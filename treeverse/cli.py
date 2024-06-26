"""Typer CLI for the treeverse library."""
from collections.abc import Callable
from collections.abc import Iterable
from pathlib import Path

import typer

from treeverse import FileNode
from treeverse import process_tree
from treeverse import reduce_tree
from treeverse import traverse_tree

app = typer.Typer()


# TODO: split into build and process
@app.command()
def traverse(  # noqa: WPS211
    path: Path = typer.Option(
        ...,
        '--path',
        '-p',
        help='Path to start the traversal',
        default_factory=Path.cwd,
    ),
    depth_limit: int = typer.Option(
        100,
        '--depth-limit',
        '-d',
        help='Maximum depth to traverse',
    ),
    extensions: list[str] = typer.Option(
        ...,
        '--extensions',
        '-e',
        help='File extensions to include (comma-separated)',
        default_factory=list,
    ),
    text_files_only: bool = typer.Option(
        True,  # noqa: WPS425
        '--text-files-only',
        '-t',
        help='Include only text files',
    ),
    filter_callback_paths: list[str] = typer.Option(
        ...,
        '--filter-callbacks',
        '-f',
        help='Paths to additional filter callback functions (module:function)',
        default_factory=list,
    ),
    payload_callback_path: str = typer.Option(
        ...,
        '--payload-callback',
        '-c',
        help='Path to the payload callback function (module:function)',
        default_factory=str,
    ),
) -> None:
    """Traverse the directory recursively, filtering and processing files."""
    filter_funcs = [
        _load_callable(path)
        for path in filter_callback_paths
    ]
    if extensions:
        filter_funcs.append(_extension_filter(extensions))

    tree = traverse_tree(
        path,
        depth_limit=depth_limit,
        filter_funcs=filter_funcs,
        text_files_only=text_files_only,
    )
    if not tree:
        typer.echo(
            'No files found matching the specified criteria.', err=True,
        )
        raise typer.Exit(code=1)

    if payload_callback_path:
        payload_callback = _load_callable(payload_callback_path)
        tree = process_tree(tree, payload_callback)

    yaml_output = tree.to_yaml()
    typer.echo(yaml_output)


@app.command()
def reduce(
    reduction_callback_path: str = typer.Option(
        ...,
        '--reduction-callback',
        '-r',
        help='Path to the reduction callback function (module:function)',
    ),
) -> None:
    """Accumulate children recursively."""
    with typer.get_text_stream('stdin') as yamlstream:
        yaml_input = typer.unstyle(yamlstream.read())
    try:
        tree = FileNode.from_yaml(yaml_input)
    except Exception as error:
        raise typer.Exit(code=1) from error
    reduction_callback = _load_callable(reduction_callback_path)
    yaml_output = reduce_tree(tree, reduction_callback).to_yaml()
    typer.echo(yaml_output)


# TODO: move out into utilities
def _load_callable(callable_path: str) -> Callable:
    module_path, callable_name = callable_path.rsplit(':', 1)
    module = __import__(module_path, fromlist=[callable_name])  # noqa: WPS421
    return getattr(module, callable_name)


# TODO: move out into default filters or something
def _extension_filter(extensions: Iterable[str]) -> Callable[[FileNode], bool]:
    extensions = {ext.lower() for ext in extensions}

    def _filter(node: FileNode) -> bool:  # noqa: WPS430
        path = node.file_info.full_path
        return path.suffix.lower()[1:] in extensions
    return _filter
