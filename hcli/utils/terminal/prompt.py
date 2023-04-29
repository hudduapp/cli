import sys
from getpass import getpass

import inquirer
import typer


def choice_prompt(message: str, choices: list) -> str:
    prompt = [inquirer.List("prompt", message=message, choices=choices)]
    res = inquirer.prompt(prompt)
    return res["prompt"]


def password_prompt(message: str):
    return getpass(message)


def confirmation_prompt(message: str = "Are you sure?"):
    res = typer.prompt(message + " (y/n)")
    if not res.lower() == "yes" and not res.lower() == "y":
        sys.exit()


def text_prompt(message: str):
    return typer.prompt(message)
