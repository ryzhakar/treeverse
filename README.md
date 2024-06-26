# Treeverse

Treeverse is a Python tool for traversing and processing file trees using custom code.

## Core Logic

1. Traverse the file tree recursively, filtering out irrelevant files.
2. Process files using custom functions.
3. Accumulate processing results from lower directory levels to higher levels.

Treeverse is designed to be flexible, allowing you to plug in your own code for filtering, processing, and accumulation.

## Installation

```bash
pip install treeverse
```

## Usage

Treeverse operates in three main steps:

1. **Traverse and Filter**:
   ```bash
   treeverse traverse --path /your/project --extensions py,js,ts \
       --filter-callbacks your_module:your_filter_function
   ```

2. **Process Files**:
   ```bash
   treeverse traverse --path /your/project --extensions py,js,ts \
       --payload-callback your_module:your_processing_function > processed_tree.yaml
   ```

3. **Accumulate Results**:
   ```bash
   cat processed_tree.yaml | treeverse reduce \
       --reduction-callback your_module:your_accumulation_function > results.yaml
   ```

You can combine these steps using pipes:

```bash
treeverse traverse --path /your/project --extensions py,js,ts \
    --payload-callback your_module:your_processing_function | \
treeverse reduce --reduction-callback your_module:your_accumulation_function > results.yaml
```

Treeverse calls your custom functions, allowing you to implement any logic for filtering, processing, and accumulation.

## Example Use Case

Process all code files in a project with a Language Model (LLM) API, and accumulate insights from lower directory levels to higher ones:

```bash
treeverse traverse --path /your/project --extensions py,js,ts \
    --payload-callback llm_processor:process_file | \
treeverse reduce --reduction-callback llm_processor:accumulate_insights > project_insights.yaml
```

In this example, `llm_processor.py` would contain custom functions for processing files with an LLM API and accumulating insights.

## Reference Implementations

For examples of callable functions that can be used with Treeverse, check the `simple_callbacks.py` file in the project repository. This file contains reference implementations for filtering, processing, and accumulation functions.
