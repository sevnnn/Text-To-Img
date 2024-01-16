from typer import BadParameter
from .tempfile import TempFile
from PIL.Image import new


def parse_file_extensions(file_extension: str) -> str:
    file_extension = file_extension.strip().lower()
    if file_extension[0] == ".":
        file_extension = file_extension[1:]

    with TempFile(file_extension) as tempfile:
        tempimage = new("RGB", (1, 1))
        try:
            tempimage.save(tempfile.name)
        except ValueError:
            raise BadParameter(f'".{file_extension}" is not a valid file extension')

    return file_extension


def test_callback() -> int:
    return 354
