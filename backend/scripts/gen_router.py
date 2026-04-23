import os

import typer

template = """
from fastapi import APIRouter, Depends

from app.api.deps import JWTDependency
# from app.services import ...

router = APIRouter(prefix="/{name}", tags=["{name}"])


@router.get(
    path="",
    summary="...",
)
async def get(jwt: JWTDependency):
    return ...
"""


def main(name: str):
    path = f"app/api/routers/{name.lower()}.py"
    if os.path.exists(path):
        print(f"File {path} already exists. Aborting to prevent overwrite.")
        return
    with open(path, "w") as f:
        f.write(template.format(name=name))


if __name__ == "__main__":
    typer.run(main)
