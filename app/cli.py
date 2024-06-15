from dotenv import load_dotenv
import os
import pathlib
from typing import Optional, Tuple

import pandas as pd
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session
import tqdm
import typer
from typing_extensions import Annotated

from app.core.db import get_async_session
from app.models import Ownership, Patent, Person
from app.parsers.patent import Parser


CHUNKSIZE = 1e3

load_dotenv()

app = typer.Typer()
db_url = os.getenv("DATABASE_URL_CLI")
engine = create_engine(db_url)


def ensure_proceed(model):
    stmt = select(func.count()).select_from(model)

    with Session(engine) as session:
        cnt = session.execute(stmt).scalar()

    if cnt > 0:
        print(
            f"Patents table already contains {cnt} records."
            " Are you sure you want to continue?"
            " New records will be added, existing will be preserved.\n"
            " y = yes, any other = exit"
        )
        task = input().strip()
        if task != "y":
            print("Okay, bye")
            return False

    return True

@app.command("load-patents")
def cli_load_patents(
    input_file: Annotated[
        pathlib.Path,
        typer.Argument(
            exists=True,
            file_okay=True,
            dir_okay=False
        )
    ]
):
    if not ensure_proceed(Patent):
        return

    print(f"Loading data from file {input_file} to patents table")

    parser = Parser(input_file)
    if not parser.setup():
        print("Incorrect input file")
        return

    with Session(engine) as session:
        for i, item in enumerate(tqdm.tqdm(parser.parse())):
            if item is None:
                continue

            record = Patent(**item)
            session.add(record)

            if i > 0 and i % 1000 == 0:
                try:
                    session.commit()
                except Exception as e:
                    session.rollback()
                    print(f"Error while trying to insert portion #{i} of data to table: {e}")

            if i > 2000:
                break

    print("Completed")


@app.command("load-persons")
def cli_load_persons(input_file: str):
    ...


@app.command("load-ownership")
def cli_load_ownership(input_file: str):
    ...


if __name__ == "__main__":
    app()
