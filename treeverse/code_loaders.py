import importlib.util  # noqa: WPS301
import sys
from pathlib import Path


def load_callable(callback_path: str):  # noqa: WPS210
    """Load arbitrary code."""
    import_error = ImportError(f'Could not load {callback_path}.')
    module_path, callable_name = callback_path.split(':')
    path = Path(module_path)
    name = path.stem
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None:
        raise import_error
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    if spec.loader is None:
        raise import_error
    spec.loader.exec_module(module)
    callable_obj = getattr(module, callable_name)
    return callable_obj
