import datetime
import pathlib

import pandas as pd

from app.parsers.common import format_tax_number


class PersonParser():
    CHUNKSIZE = 1e3
    IT_AC_CODES = ["62.01", "62.02", "62.02.1", "62.02.4", "62.03.13", "62.09", "63.11.1"]

    def __init__(self, df_path: pathlib.Path):
        self._df_path = df_path

    def _get_category(self, name: str, activity_code: str) -> str:
        if activity_code in self.IT_AC_CODES:
            return "ИТ-компания"

        return "Прочие организации"

    def _parse_row(self, row: pd.Series) -> dict:
        row = row.fillna("")

        tax_number = format_tax_number(row["ИНН"])

        if row["ОКОПФ (расшифровка)"] == "Индивидуальные предприниматели":
            kind = 2
        else:
            kind = 1

        try:
            reg_date = datetime.datetime.fromisoformat(
                row["creation_date"]).date()
        except:
            reg_date = None

        category = self._get_category(row["Наименование полное"], row["ОКВЭД2"])

        return dict(
            kind=kind,
            tax_number=tax_number,
            full_name=row["Наименование полное"],
            short_name=row["Наименование краткое"],
            legal_address=row["Юр адрес"],
            fact_address=row["Факт адрес"],
            reg_date=reg_date,
            active=row["Компания действующая (1) или нет (0)"] == "1",
            category=category,
        )

    def parse(self):
        df = pd.read_csv(self._df_path, sep=";", dtype=str, chunksize=self.CHUNKSIZE)

        for chunk in df:
            chunk.dropna(subset=["Наименование полное", "ИНН"], how="any", inplace=True)
            chunk = chunk.loc[chunk["Головная компания (1) или филиал (0)"] == '1', :].copy()
            chunk.drop_duplicates(subset=["ИНН"], inplace=True)

            for _, row in chunk.iterrows():
                data = self._parse_row(row)
                yield data

    def setup(self):
        print("Setting up parser")
        df = pd.read_csv(self._df_path, sep=";", chunksize=self.CHUNKSIZE)
        chunk = df.get_chunk(1)

        if "ИНН" not in chunk.columns:
            print("Column 'ИНН' not found in data")
            return False

        print("Data seems to be correct")

        return True

