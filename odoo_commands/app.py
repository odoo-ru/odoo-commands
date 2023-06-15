import typer
from odoo_commands.createdb import create_database

app = typer.Typer()

app.command()(create_database)

@app.command()
def hello(name: str):
    print(f"Hello {name}")


@app.command()
def goodbye(name: str, formal: bool = False):
    if formal:
        print(f"Goodbye Ms. {name}. Have a good day.")
    else:
        print(f"Bye {name}!")


@app.command()
def create(user_name: str):
    print(f"Creating user: {user_name}")


if __name__ == "__main__":
    app()
