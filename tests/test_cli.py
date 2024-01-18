from os import listdir, mkdir, remove, rmdir
from os.path import exists, join
from typing import Union

from pytest import mark
from typer.testing import CliRunner

from text_to_img import app

runner = CliRunner()


def test_help() -> None:
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "File Options" in result.stdout


@mark.parametrize(
    "text, argument_value, expected_output",
    [
        ("test", -1, {"code": 2, "in_message": "Error"}),
        ("test", "not a number", {"code": 2, "in_message": "Error"}),
        ("test", 1, {"code": 0, "in_message": "Generated"}),
    ],
)
def test_font_size(
    text: str,
    argument_value: Union[int, str],
    expected_output: dict,
) -> None:
    result = runner.invoke(app, [text, "--font-size", argument_value])  # type: ignore

    assert result.exit_code == expected_output["code"]
    assert expected_output["in_message"] in result.stdout

    if expected_output["code"] == 0:
        assert exists(f"./{text}.png")
        remove(f"./{text}.png")


@mark.parametrize(
    "text, argument_value, expected_output",
    [
        ("test", "arial.ttf", {"code": 0, "in_message": "Generated"}),
        ("test", "Arial", {"code": 0, "in_message": "Generated"}),
        ("test", "nonexistant font", {"code": 2, "in_message": "Error"}),
        ("test", "", {"code": 2, "in_message": "Error"}),
        ("test", "invalid/font/name", {"code": 2, "in_message": "Error"}),
    ],
)
def test_font_name(text: str, argument_value: str, expected_output: dict) -> None:
    result = runner.invoke(app, [text, "--font-name", argument_value])

    assert result.exit_code == expected_output["code"]
    assert expected_output["in_message"] in result.stdout

    if expected_output["code"] == 0:
        assert exists(f"./{text}.png")
        remove(f"./{text}.png")


@mark.parametrize(
    "text, argument_value, expected_output",
    [
        ("test", "0,0,0", {"code": 0, "in_message": "Generated"}),
        ("test", "0,0,0,0", {"code": 0, "in_message": "Generated"}),
        ("test", "0 , 0 , 0", {"code": 0, "in_message": "Generated"}),
        ("test", "0 , 0 , 0 , 0", {"code": 0, "in_message": "Generated"}),
        ("test", "#FFFFFF", {"code": 0, "in_message": "Generated"}),
        ("test", "#FFFFFFFF", {"code": 0, "in_message": "Generated"}),
        ("test", "white", {"code": 0, "in_message": "Generated"}),
        ("test", "300,300,300", {"code": 0, "in_message": "Generated"}),
        ("test", "300,300,300,300", {"code": 0, "in_message": "Generated"}),
        ("test", "#HHHHHH", {"code": 2, "in_message": "Error"}),
        ("test", "#HHHHHHHH", {"code": 2, "in_message": "Error"}),
        ("test", "not a color", {"code": 2, "in_message": "Error"}),
        ("test", "", {"code": 2, "in_message": "Error"}),
        ("test", "-1, -1, -1", {"code": 2, "in_message": "Error"}),
    ],
)
def test_font_color(text: str, argument_value: str, expected_output: dict) -> None:
    result = runner.invoke(app, [text, "--font-color", argument_value])

    assert result.exit_code == expected_output["code"]
    assert expected_output["in_message"] in result.stdout

    if expected_output["code"] == 0:
        assert exists(f"./{text}.png")
        remove(f"./{text}.png")


@mark.parametrize(
    "text, argument_value, expected_output",
    [
        ("test", "0,0,0", {"code": 0, "in_message": "Generated"}),
        ("test", "0,0,0,0", {"code": 0, "in_message": "Generated"}),
        ("test", "0 , 0 , 0", {"code": 0, "in_message": "Generated"}),
        ("test", "0 , 0 , 0 , 0", {"code": 0, "in_message": "Generated"}),
        ("test", "#FFFFFF", {"code": 0, "in_message": "Generated"}),
        ("test", "#FFFFFFFF", {"code": 0, "in_message": "Generated"}),
        ("test", "white", {"code": 0, "in_message": "Generated"}),
        ("test", "300,300,300", {"code": 0, "in_message": "Generated"}),
        ("test", "300,300,300,300", {"code": 0, "in_message": "Generated"}),
        ("test", "#HHHHHH", {"code": 2, "in_message": "Error"}),
        ("test", "#HHHHHHHH", {"code": 2, "in_message": "Error"}),
        ("test", "not a color", {"code": 2, "in_message": "Error"}),
        ("test", "", {"code": 2, "in_message": "Error"}),
        ("test", "-1, -1, -1", {"code": 2, "in_message": "Error"}),
    ],
)
def test_background_color(
    text: str, argument_value: str, expected_output: dict
) -> None:
    result = runner.invoke(app, [text, "--background-color", argument_value])

    assert result.exit_code == expected_output["code"]
    assert expected_output["in_message"] in result.stdout

    if expected_output["code"] == 0:
        assert exists(f"./{text}.png")
        remove(f"./{text}.png")


@mark.parametrize(
    "text, argument_value, expected_output",
    [
        ("test", "png", {"code": 0, "in_message": "Generated"}),
        ("test", ".png", {"code": 0, "in_message": "Generated"}),
        ("test", " .png ", {"code": 0, "in_message": "Generated"}),
        ("test", "not a valid file extension", {"code": 2, "in_message": "Error"}),
    ],
)
def test_file_extension(text: str, argument_value: str, expected_output: dict) -> None:
    result = runner.invoke(app, [text, "--file-extension", argument_value])

    assert result.exit_code == expected_output["code"]
    assert expected_output["in_message"] in result.stdout

    if expected_output["code"] == 0:
        assert exists(f"./{text}.png")
        remove(f"./{text}.png")


@mark.parametrize(
    "text, argument_value, expected_output",
    [
        ("test", ".", {"code": 0, "in_message": "Generated"}),
        ("test", "./output/", {"code": 0, "in_message": "Generated"}),
        ("test", " ./output/ ", {"code": 0, "in_message": "Generated"}),
        ("test", "not/a/valid/path", {"code": 2, "in_message": "Error"}),
    ],
)
def test_output_path(text: str, argument_value: str, expected_output: dict) -> None:
    stripped_argument_value = argument_value.strip()
    if expected_output["code"] == 0:
        if not exists(stripped_argument_value):
            mkdir(stripped_argument_value)

    result = runner.invoke(app, [text, "--output-path", argument_value])
    assert result.exit_code == expected_output["code"]
    assert expected_output["in_message"] in result.stdout

    if expected_output["code"] == 0:
        genereted_file_path = join(stripped_argument_value, f"{text}.png")

        assert exists(genereted_file_path)
        remove(genereted_file_path)
        if len(listdir(stripped_argument_value)) == 0:
            rmdir(stripped_argument_value)


@mark.parametrize(
    "text, argument_value, expected_output",
    [
        ("test", "valid file name", {"code": 0, "in_message": "Generated"}),
        ("test", "not/a/valid/file/name", {"code": 2, "in_message": "Error"}),
        ("test", "", {"code": 2, "in_message": "Error"}),
    ],
)
def test_file_name(text: str, argument_value: str, expected_output: dict) -> None:
    result = runner.invoke(app, [text, "--file-name", argument_value])

    assert result.exit_code == expected_output["code"]
    assert expected_output["in_message"] in result.stdout

    if expected_output["code"] == 0:
        assert exists(f"./{argument_value}.png")
        assert not exists(f"./{text}.png")
        remove(f"./{argument_value}.png")
