# Treeverse

Treeverse is a Python tool for traversing and processing file trees using custom code.

## Installation

```bash
pip install treeverse
```

## Usage

Treeverse operates in two main steps:

1. **Traverse and Process**:
   ```bash
   treeverse traverse -p /path/to/your/project -e py -e yaml \
       -c your_module.py:your_processing_function > processed_tree.yaml
   ```

   Options:
   - `-p, --path`: Specify the path to traverse (default is current directory)
   - `-e, --extensions`: Specify file extensions to include (can be used multiple times)
   - `-c, --callback`: Path to the module and function for processing (module.py:function)

2. **Reduce Results** (if needed):
   ```bash
   cat processed_tree.yaml | treeverse reduce \
       -c your_module.py:your_reduction_function > results.yaml
   ```

   Options:
   - `-c, --callback`: Path to the module and function for reduction

## Example Use Case

Process all Python and YAML files in a project with a custom analysis function:

```bash
treeverse traverse -p ~/path/to/your/project -e py -e yaml \
    -c ~/path/to/your/tools.py:llm_analysis > project_analysis.yaml
```

In this example, `tools.py` would contain a custom `llm_analysis` function for processing files.

## Reference Implementations

For examples of callable functions that can be used with Treeverse, check the `simple_callbacks.py` file in the project repository. This file contains reference implementations for processing and reduction functions.
