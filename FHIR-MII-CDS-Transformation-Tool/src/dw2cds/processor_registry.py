from __future__ import annotations

import importlib
import inspect
import logging
import os
import pathlib
import sys
from typing import Callable

"""
This module provides a registry to hold custom data processors.
"""

logger = logging.getLogger(__name__)


class ProcessorRegistry:
    """
    Registry to hold custom data processors.

    Methods:
        register(name: str, processor: Callable[[Union[str, int, float]], Union[str, int, float]]):
            Registers a custom processor.
        get_processor(name: str) -> Callable[[Union[str, int, float]], Union[str, int, float]]:
            Retrieves a processor by name.
        get_processors() -> dict[str, Callable[[Union[str, int, float]], Union[str, int, float]]]:
            Retrieves all processors.
        get_processor_args(name: str) -> list[str] or None:
            Retrieves the arguments of a processor by name.
    """

    def __init__(
        self,
        processor_paths: list[str | os.PathLike],
    ) -> None:
        """
        Initializes the ProcessorRegistry.

        Args:
            processor_paths (list[str | os.PathLike]): List of paths to custom processor modules.
        """
        self._processors = {}
        logger.debug(
            f"As processors are defined {processor_paths} of type {type(processor_paths)}",
        )
        self.load_processors(processor_paths)

    def load_processors(self, paths: list[str | os.PathLike]) -> None:
        """
        Loads custom processors from the specified paths.
        """
        for path in paths:
            module_path = pathlib.Path(path)
            parent_dir = str(module_path.parent.resolve())
            if parent_dir not in sys.path:
                print(f"Adding {parent_dir} to sys.path")  # Add debugging print
                sys.path.insert(0, parent_dir)  # Use insert(0, ...) to prioritize this path

            module_name = module_path.stem
            try:
                print(f"Trying to import module: {module_name}")
                print(f"Trying to import module from: {module_path}")

                module = importlib.import_module(module_name)
            except ModuleNotFoundError as e:
                print(f"Error importing module {module_name}: {e}")
                continue

            for name, obj in inspect.getmembers(module):
                if name.startswith("process_"):
                    self.register(name, obj)
                    print(f"Registered processor: {name}")

    def register(
        self,
        name: str,
        processor: Callable[[str | int | float], str | int | float],
    ) -> None:
        """
        Registers a custom processor.

        Args:
            name (str): The name of the processor.
            processor (Callable[[str | int | float], str | int | float]): The processor function.
        """
        self._processors[name] = processor

    def get_processor(
        self,
        name: str,
    ) -> Callable[[str | int | float], str | int | float]:
        """
        Retrieves a processor by name.

        Args:
            name (str): The name of the processor.

        Returns:
            Callable[[str | int | float], str | int | float]: The processor function.
        """
        return self._processors.get(name)

    def get_processors(
        self,
    ) -> dict[str, Callable[[str | int | float], str | int | float]]:
        """
        Retrieves all processors.

        Returns:
            dict[str, Callable[[str | int | float], str | int | float]]: The processors.
        """
        return self._processors

    def get_processor_args(self, name: str) -> list[str] or None:
        """
        Retrieves the arguments of a processor by name.

        Args:
            name (str): The name of the processor.

        Returns:
            list[str] or None: The arguments of the processor.
        """
        processor = self.get_processor(name)
        if processor:
            sig = inspect.signature(processor)
            return [param.name for param in sig.parameters.values()]
        return None


if __name__ == "__main__":
    ProcessorRegistry()
