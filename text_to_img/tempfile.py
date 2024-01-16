from io import TextIOWrapper
from os import remove, urandom
from os.path import join
from tempfile import gettempdir
from typing import Any, Optional, Type


class TempFile:
    def __init__(self, file_extension: str, file_name: str = urandom(16).hex()) -> None:
        self.tempfile_path = join(gettempdir(), f"{file_name}.{file_extension}")

    def __enter__(self) -> TextIOWrapper:
        self.opened_file = open(self.tempfile_path, "w")

        return self.opened_file

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[Any],
    ) -> None:
        self.opened_file.close()
        remove(self.tempfile_path)
