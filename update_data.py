"""Download the latest monthly price history of the PEE funds and the Livret A rates.

PEE funds: the export link of each fund needs a `ddp` token, which is embedded in the public page of the fund,
so the page is fetched first to read it. This is not a documented API: every file is checked
before replacing the one in `data/`, and the script stops at the first unexpected answer.

Livret A: the Banque de France series, from the public DBnomics API (Webstat needs an API key). It
is saved in the same format as the Webstat CSV export.

Usage: ./.venv/bin/python update_data.py
"""

import io
import json
import re
import time
import tomllib
import urllib.request
from datetime import date
from pathlib import Path

import pandas as pd

BASE_URL = "https://www.creditmutuel-am.eu/fr/institutionnels/nos-fonds/"
DATA_DIR = Path(__file__).parent / "data"
XLSX_CONTENT_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
LIVRET_A_SERIES = "MIR1.M.FR.B.L23FRLA.D.R.A.2230U6.EUR.O"
LIVRET_A_URL = f"https://api.db.nomics.world/v22/series/BDF/MIR1/{LIVRET_A_SERIES.removeprefix('MIR1.')}?observations=1"

# data file name (without extension) -> ISIN
with (Path(__file__).parent / "consts.toml").open("rb") as f:
    FUNDS = {fund["file"]: fund["isin"] for fund in tomllib.load(f)["PEE_FUNDS"]}


def fetch(url: str) -> tuple[bytes, str]:
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read(), response.headers.get_content_type()


def export_token(isin: str) -> str:
    html, _ = fetch(f"{BASE_URL}VALE_Fiche.aspx?Isin={isin}")
    tokens = set(re.findall(r"ddp=([A-Za-z0-9_-]+)", html.decode("utf-8", "replace")))
    if len(tokens) != 1:
        raise RuntimeError(f"{isin}: expected one export token in the fund page, found {len(tokens)}")
    return tokens.pop()


def last_date(sheet: pd.DataFrame) -> pd.Timestamp:
    # the most recent price is the first row after the header
    return pd.to_datetime(sheet.iloc[7, 0], format="%d/%m/%Y")


def check(name: str, isin: str, sheet: pd.DataFrame, old: pd.DataFrame) -> None:
    """Make sure the file has the layout the notebook expects and is not older than the current one"""
    problems = []
    if sheet.iloc[6, 0] != "Date de cotation" or sheet.iloc[6, 1] != "Dernier cours en EUR":
        problems.append(f"unexpected header {sheet.iloc[6, :2].tolist()}")
    if str(sheet.iloc[4, 4]).zfill(12) != isin:
        problems.append(f"ISIN {sheet.iloc[4, 4]} instead of {isin}")
    if sheet.iloc[-1, 0] != "Se rendre en haut du document":
        problems.append(f"unexpected footer {sheet.iloc[-1, 0]!r}")
    if not problems and last_date(sheet) < last_date(old):
        problems.append(f"latest price {last_date(sheet).date()} older than {last_date(old).date()}")
    if not problems and len(sheet) < len(old):
        problems.append(f"{len(sheet)} rows instead of at least {len(old)}")
    if problems:
        raise RuntimeError(f"{name}: " + ", ".join(problems))


def livret_a(old_path: Path) -> bytes | None:
    """Return the new Livret A CSV, or None if there are no new rates"""
    content, _ = fetch(LIVRET_A_URL)
    series = json.loads(content)["series"]["docs"][0]
    if series["series_code"] != LIVRET_A_SERIES.removeprefix("MIR1."):
        raise RuntimeError(f"Livret A: got series {series['series_code']}")
    rates = pd.Series(series["value"], index=pd.PeriodIndex(series["period"], freq="M"), dtype=float)
    old = pd.read_csv(old_path, sep=";", skiprows=6, names=["date", "rate"], decimal=",",
                      parse_dates=["date"], index_col="date")["rate"]
    old.index = old.index.to_period("M")
    # the rates are set by the government and never revised, the old ones must all be there
    if not old.equals(rates.reindex(old.index)):
        raise RuntimeError("Livret A: the past rates differ from the current file")
    if len(rates) == len(old):
        print(f"Livret A: up to date ({old.index.max()})")
        return None
    print(f"Livret A: {old.index.max()} -> {rates.index.max()} ({len(rates) - len(old):+d} rows)")
    # keep the Webstat export layout: same header, end of month dates, newest first, decimal comma
    header = old_path.read_text(encoding="utf-8-sig").splitlines()[:6]
    rows = [f"{period.end_time:%Y-%m-%d};{str(rate).replace('.', ',')}"
            for period, rate in rates.sort_index(ascending=False).items()]
    return "\r\n".join(header + rows).encode("utf-8-sig") + b"\r\n"


def main() -> None:
    today = date.today().strftime("%Y%m%d")
    # download and check everything first, so that a failure does not leave the data half updated
    downloads = {}
    for name, isin in FUNDS.items():
        content, content_type = fetch(
            f"{BASE_URL}VALE_FicheHistoriqueCours.aspx?ddp={export_token(isin)}&pr=M&dateb={today}&export=2")
        if content_type != XLSX_CONTENT_TYPE:
            raise RuntimeError(f"{name}: got {content_type} instead of an xlsx file")
        sheet = pd.read_excel(io.BytesIO(content), header=None)
        old = pd.read_excel(DATA_DIR / f"{name}.xlsx", header=None)
        check(name, isin, sheet, old)
        # the header contains the export date, only the prices tell if there is something new
        if sheet.iloc[6:].equals(old.iloc[6:]):
            print(f"{name}: up to date ({last_date(old).date()})")
        else:
            downloads[f"{name}.xlsx"] = content
            print(f"{name}: {last_date(old).date()} -> {last_date(sheet).date()} ({len(sheet) - len(old):+d} rows)")
        # be gentle with the website
        time.sleep(1)

    if content := livret_a(DATA_DIR / "LIVRET_A.csv"):
        downloads["LIVRET_A.csv"] = content

    for file, content in downloads.items():
        (DATA_DIR / file).write_bytes(content)
    print(f"Updated {len(downloads)} files in {DATA_DIR}")


if __name__ == "__main__":
    main()
