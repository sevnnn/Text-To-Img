from subprocess import run


def csfix() -> None:
    run(
        [
            "autoflake",
            "--in-place",
            "--recursive",
            "--remove-duplicate-keys",
            "--remove-unused-variables",
            "--remove-all-unused-imports",
            ".",
        ],
        check=True,
    )
    run(["isort", "."], check=True)
    run(["black", "."], check=True)
