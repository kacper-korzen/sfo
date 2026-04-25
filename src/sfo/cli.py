import typer

from .backup import app as backup_app
from .organizer import app as organizer_app
from .restore import app as restore_app

app = typer.Typer()

app.add_typer(organizer_app)
app.add_typer(backup_app)
app.add_typer(restore_app)


if __name__ == "__main__":
    app()
