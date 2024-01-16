from typer import BadParameter
from .tempfile import TempFile
from PIL.Image import new
from os.path import exists


def parse_generic_text(text: str) -> str:
    return text.strip().lower()


def parse_file_extensions(file_extension: str) -> str:
    file_extension = parse_generic_text(file_extension)
    if file_extension[0] == ".":
        file_extension = file_extension[1:]

    with TempFile(file_extension) as tempfile:
        tempimage = new("RGB", (1, 1))
        try:
            tempimage.save(tempfile.name)
        except ValueError:
            raise BadParameter(f'".{file_extension}" is not a valid file extension')

    return file_extension


def parse_output_path(output_path: str) -> str:
    if not exists(output_path):  # type: ignore
        raise BadParameter(f"Selected output folder ({output_path}) does not exist")

    return output_path


def parse_file_name(file_name: str) -> str:
    file_name = parse_generic_text(file_name)
    try:
        with TempFile("", file_name):
            pass
    except OSError:
        raise BadParameter(f'"{file_name}" is not a valid file name')

    return file_name
