import typer
from odoo_commands.createdb import create_database

app = typer.Typer()

app.command(name='createdb')(create_database)

@app.command()
def hello(name: str):
    print(f"Hello {name}")


if __name__ == "__main__":
    app()
