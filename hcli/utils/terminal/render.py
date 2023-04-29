from typing import Union

import rich.table
from rich import print as rprint


def print(message: Union[str, rich.table.Table], type: str = "info"):
    if type == "info":
        rprint(f"[white]{message}[white]")
    if type == "error":
        rprint(f"[red]{message}[red]")
    if type == "warning":
        rprint(f"[yellow]{message}[yellow]")
    if type == "success":
        rprint(f"[green]{message}[green]")
    if type == "table":
        rprint(message)
