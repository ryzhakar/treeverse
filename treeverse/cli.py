"""Typer CLI for the treeverse library."""
from collections.abc import Callable
from collections.abc import Iterable
from pathlib import Path

import typer

from treeverse import FileNode
from treeverse import process_tree
from treeverse import reduce_tree
from treeverse import traverse_tree
from treeverse.code_loaders import load_callable

app = typer.Typer()


@app.command()
def build(
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
        help='File extensions to include',
        default_factory=list,
    ),
    text_files_only: bool = typer.Option(
        True,
        '--text-files-only',
        '-t',
        help='Include only text files',
        is_flag=False,
    ),
    filter_callback_paths: list[str] = typer.Option(
        ...,
        '--callback',
        '-c',
        help='Paths to additional filter callback functions (module:function)',
        default_factory=list,
    ),
    output_file: str = typer.Option(
        'tree.yaml',
        '--output',
        '-o',
        help='Output file',
    ),
    write_to_stream: bool = typer.Option(
        False,
        '--write-to-stream',
        help='Write output to stdout instead of a file',
    ),
) -> None:
    """Build the directory tree, filtering files."""
    filter_funcs = [load_callable(path) for path in filter_callback_paths]
    if extensions:
        filter_funcs.append(_extension_filter(extensions))

    tree = traverse_tree(
        path,
        depth_limit=depth_limit,
        filter_funcs=filter_funcs,
        text_files_only=text_files_only,
    )
    if not tree:
        typer.echo('No files found matching the specified criteria.', err=True)
        raise typer.Exit(code=1)

    yaml_output = tree.to_yaml()
    _write_output(yaml_output, output_file, write_to_stream)


@app.command()
def process(
    input_file: str = typer.Option(
        'tree.yaml',
        '--input',
        '-i',
        help='Input file',
    ),
    output_file: str = typer.Option(
        'processed_tree.yaml',
        '--output',
        '-o',
        help='Output file',
    ),
    payload_callback_path: str = typer.Option(
        ...,
        '--callback',
        '-c',
        help='Path to the payload callback function (module:function)',
    ),
    read_from_stream: bool = typer.Option(
        False,
        '--read-from-stream',
        help='Read input from stdin instead of a file',
    ),
    write_to_stream: bool = typer.Option(
        False,
        '--write-to-stream',
        help='Write output to stdout instead of a file',
    ),
) -> None:
    """Process the tree with a payload callback."""
    yaml_input = _read_input(input_file, read_from_stream)
    try:
        tree = FileNode.from_yaml(yaml_input)
    except Exception as error:
        typer.echo(f'Error parsing input: {error}', err=True)
        raise typer.Exit(code=1) from error

    payload_callback = load_callable(payload_callback_path)
    processed_tree = process_tree(tree, payload_callback)
    yaml_output = processed_tree.to_yaml()
    _write_output(yaml_output, output_file, write_to_stream)


@app.command()
def accumulate(
    input_file: str = typer.Option(
        'processed_tree.yaml',
        '--input',
        '-i',
        help='Input file',
    ),
    output_file: str = typer.Option(
        'accumulated_tree.yaml',
        '--output',
        '-o',
        help='Output file',
    ),
    accumulation_callback_path: str = typer.Option(
        ...,
        '--callback',
        '-c',
        help='Path to the accumulation callback function (module:function)',
    ),
    read_from_stream: bool = typer.Option(
        False,
        '--read-from-stream',
        help='Read input from stdin instead of a file',
    ),
    write_to_stream: bool = typer.Option(
        False,
        '--write-to-stream',
        help='Write output to stdout instead of a file',
    ),
) -> None:
    """Accumulate results from children to parents."""
    yaml_input = _read_input(input_file, read_from_stream)
    try:
        tree = FileNode.from_yaml(yaml_input)
    except Exception as error:
        typer.echo(f'Error parsing input: {error}', err=True)
        raise typer.Exit(code=1) from error

    accumulation_callback = load_callable(accumulation_callback_path)
    accumulated_tree = reduce_tree(tree, accumulation_callback)
    yaml_output = accumulated_tree.to_yaml()
    _write_output(yaml_output, output_file, write_to_stream)


def _extension_filter(extensions: Iterable[str]) -> Callable[[FileNode], bool]:
    extensions = {ext.lower() for ext in extensions}

    def filter_by_extension(node: FileNode) -> bool:  # noqa: WPS430
        path = node.file_info.full_path
        return path.suffix.lower()[1:] in extensions

    return filter_by_extension


def _read_input(input_file: str, read_from_stream: bool) -> str:
    """Read input from file or stdin."""
    if read_from_stream:
        return typer.get_text_stream('stdin').read()
    with open(input_file) as input_stream:
        return input_stream.read()


def _write_output(
    payload: str,
    output_file: str,
    write_to_stream: bool,
) -> None:
    """Write output to file or stdout."""
    if write_to_stream:
        typer.echo(payload)
    with open(output_file, 'w') as output_stream:
        output_stream.write(payload)
