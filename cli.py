from asyncio import run

from typer import Typer, confirm

from tests.populate_data import create_data

app = Typer()


@app.command()
def populate_data(count: int = 10):
    confirm(f"You are about to generate {count} results, are you OK?", abort=True)
    run(create_data(count=count))


if __name__ == "__main__":
    app()
