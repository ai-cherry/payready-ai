"""Minimal secrets management CLI backed by macOS Keychain."""

from __future__ import annotations

import typer
import keyring

SERVICE = "payready"

app = typer.Typer(no_args_is_help=True, help="Store and inspect secrets in the macOS Keychain")


@app.command("set")
def set_key(name: str, value: str | None = typer.Option(None, "--value", "-v")) -> None:
    """Persist a secret value in the Keychain."""

    if value is None:
        value = typer.prompt(f"Enter value for {name}", hide_input=True)
    keyring.set_password(SERVICE, name, value)
    typer.echo(f"saved: {name}")


@app.command("get")
def get_key(name: str, show: bool = typer.Option(False, "--show")) -> None:
    """Retrieve a stored secret; hide by default."""

    value = keyring.get_password(SERVICE, name)
    if not value:
        raise typer.Exit(code=1)
    if show:
        typer.echo(value)
    else:
        typer.echo(f"{name}=***{value[-4:]}")


@app.command("rm")
def remove_key(name: str) -> None:
    """Delete a secret from the Keychain."""

    keyring.delete_password(SERVICE, name)
    typer.echo(f"removed: {name}")


if __name__ == "__main__":  # pragma: no cover - convenience entrypoint
    app()
