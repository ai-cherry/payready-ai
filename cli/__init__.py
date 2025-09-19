"""Unified CLI package entry point exporting the Typer application."""

def get_app():
    """Lazy load the Typer app to avoid circular imports."""
    from .cli import app
    return app

__all__ = ["get_app"]
