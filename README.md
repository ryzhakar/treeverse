# Treeverse

Treeverse is a Python tool for traversing, processing, and accumulating data from file trees using custom code.

## Installation

```bash
pip install treeverse
```

## Usage

Treeverse operates in three main steps:

1. **Build**: Traverse the directory and build the file tree
2. **Process**: Apply custom processing to each node
3. **Accumulate**: Aggregate data from child nodes to parent nodes

### 1. Build the tree

```bash
treeverse build -p /path/to/your/project -e py -e yaml \
    -c your_module:your_filter_function -o tree.yaml
```

Options:
- `-p, --path`: Specify the path to traverse (default is current directory)
- `-e, --extensions`: Specify file extensions to include (can be used multiple times)
- `-c, --callback`: Path to filter callback functions (can be used multiple times)
- `-o, --output`: Output file (default: tree.yaml)
- `--write-to-stream`: Write output to stdout instead of a file

### 2. Process the tree

```bash
treeverse process -i tree.yaml -c your_module:your_processing_function -o processed_tree.yaml
```

Options:
- `-i, --input`: Input file (default: tree.yaml)
- `-c, --callback`: Path to the processing function
- `-o, --output`: Output file (default: processed_tree.yaml)
- `--read-from-stream`: Read input from stdin instead of a file
- `--write-to-stream`: Write output to stdout instead of a file

### 3. Accumulate results

```bash
treeverse accumulate -i processed_tree.yaml -c your_module:your_accumulation_function -o final_result.yaml
```

Options:
- `-i, --input`: Input file (default: processed_tree.yaml)
- `-c, --callback`: Path to the accumulation function
- `-o, --output`: Output file (default: accumulated_tree.yaml)
- `--read-from-stream`: Read input from stdin instead of a file
- `--write-to-stream`: Write output to stdout instead of a file

## Example Use Case

Process all Python and YAML files in a project, analyze them, and accumulate results:

```bash
treeverse build -p ~/path/to/your/project -e py -e yaml -o tree.yaml
treeverse process -i tree.yaml -c ~/path/to/your/tools.py:analyze_file -o processed_tree.yaml
treeverse accumulate -i processed_tree.yaml -c ~/path/to/your/tools.py:accumulate_results -o final_analysis.yaml
```

To use streaming for the entire pipeline:

```bash
treeverse build -p ~/path/to/your/project -e py -e yaml --write-to-stream | \
treeverse process -c ~/path/to/your/tools.py:analyze_file --read-from-stream --write-to-stream | \
treeverse accumulate -c ~/path/to/your/tools.py:accumulate_results --read-from-stream > final_analysis.yaml
```

In this example, `tools.py` would contain custom `analyze_file` and `accumulate_results` functions.

## Reference Implementations

For examples of callable functions that can be used with Treeverse, check the `simple_callbacks.py` file in the project repository. This file contains reference implementations for filtering, processing, and accumulation functions.
