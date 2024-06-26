"""Simple callback functions for Treeverse."""
from treeverse import FileNode


def process_line_count(node: FileNode) -> dict:
    """Add line count to the node's custom data."""
    if node.file_info.is_text_file:
        return {'lines': node.file_info.line_count}
    return {}


def reduce_total_lines(node: FileNode) -> dict:
    """Calculate total line count in the tree."""
    parent_lines = node.custom_data.get('lines', 0)
    children_lines = sum(
        child.custom_data.get('lines', 0)
        for child in node.child_nodes
    )
    return {'custom_data': {'lines': parent_lines + children_lines}}
