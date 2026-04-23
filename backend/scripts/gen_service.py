import os

import typer

template = """
from fastapi import Depends

from app.db.sql import SessionDependency

class {name}Service:
    def __init__(
        self,
        session: SessionDependency,
        _repo: ... = Depends(),
    ):
        self.session = session

    def foo(self) -> None:
        pass

"""


def main(name: str):
    path = f"app/services/{name.lower()}_service.py"
    if os.path.exists(path):
        print(f"File {path} already exists. Aborting to prevent overwrite.")
        return
    with open(path, "w") as f:
        f.write(template.format(name=name))


if __name__ == "__main__":
    typer.run(main)
