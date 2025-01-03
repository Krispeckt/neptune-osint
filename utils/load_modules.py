from __future__ import annotations

import importlib.machinery
import os
from types import ModuleType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .abc import BaseModule

__all__ = [
    "load_module",
    "collect_modules"
]


class ModuleLoadingError(Exception):
    """Custom exception for module loading errors."""


class DirectoryError(Exception):
    """Custom exception for directory-related errors."""


def load_module(module_path: str) -> ModuleType:
    """Loads a module from a file at the given path."""
    try:
        module_name = os.path.splitext(os.path.basename(module_path))[0]
        spec = importlib.machinery.SourceFileLoader(module_name, module_path)
        module = spec.load_module()
        return module
    except FileNotFoundError:
        raise ModuleLoadingError(f"File {module_path} not found.")
    except ImportError as _e:
        raise ModuleLoadingError(f"Import error in module {module_path}: {_e}")
    except SyntaxError as _e:
        raise ModuleLoadingError(f"Syntax error in file {module_path}: {_e}")
    except Exception as _e:
        raise ModuleLoadingError(f"Unknown error while loading module {module_path}: {_e}")


def collect_modules(directory: str) -> dict[str, list[BaseModule]]:
    modules_dict = {}

    try:
        for folder_path, _, filenames in os.walk(directory):
            module_list = []

            for filename in filenames:
                if filename.endswith(".py"):
                    file_path = os.path.join(folder_path, filename)
                    module = load_module(file_path)

                    if module is not None:
                        if hasattr(module, 'load'):
                            try:
                                module_list.append(module.load())
                            except Exception as _e:
                                raise ModuleLoadingError(f"Error calling load() in module {filename}: {_e}")

            if module_list:
                relative_folder = os.path.relpath(folder_path, directory)
                modules_dict[relative_folder] = module_list

    except FileNotFoundError:
        raise DirectoryError(f"Directory {directory} not found.")
    except PermissionError:
        raise DirectoryError(f"No permission to access directory {directory}.")
    except OSError as _e:
        raise DirectoryError(f"OS error accessing directory {directory}: {_e}")
    except Exception as _e:
        raise DirectoryError(f"Unknown error while collecting modules from {directory}: {_e}")

    return modules_dict