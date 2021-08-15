import csv
from pathlib import Path
from devtools import debug
from typing import List
from datetime import datetime
import re


def parse_header(lines: List[str]) -> dict:
    """Parse header."""
    # written to be readable by people beginning python, so rather verbose.
    data = {}
    match = re.search(r"MCD_(.+) with (.+).", lines[1])
    if match:
        data["mcd_version"] = match.group(1)
        data["model"] = match.group(2)
    match = re.search(r"Ls (.+). Altitude (.+) ALS Local time (.+)", lines[2])
    if match:
        data["ls"] = match.group(1)
        data["altitude"] = match.group(2)
        data["local_time"] = match.group(3).strip()
    assert "-" * 6 in lines[3]
    match = re.search(r"Column 1 is (.+)", lines[4])
    if match:
        data["column_1"] = match.group(1)

    match = re.search(r"Columns 2\+ are (.+)", lines[5])
    if match:
        data["variable"] = match.group(1)

    match = re.search(r"Line 1 is (.+)", lines[6])
    if match:
        data["keys"] = match.group(1)
    assert "-" * 6 in lines[7]
    match = re.search(r"Retrieved on: (.+)", lines[8])
    if match:
        data["retrieval_date"] = datetime.fromisoformat(match.group(1))
    return data


def read_ascii_data(dataf):
    sections = {}
    headers = []
    datas = []
    parsing_header = False
    parsing_data = False
    with dataf.open() as f:
        for row in f.read():
            if "#" * 8 in row:  # start header section
                parsing_header = True
                header += row
                continue
            while parsing_header:
                header += row

            if "#" * 8 in row:
                parsing_header = False
                parsing_data = True

            parsed = parse_header(header)
            sections["keys"] = parsed
            header = []


# inf = Path("~/Downloads/data.txt").expanduser()
# read_ascii_data(inf)


def test_parse_header():
    data = """##########################################################################################
### MCD_v5.3 with climatology average solar scenario.
### Ls 85.3deg. Altitude 10.0 m ALS Local time 0.0h (at longitude 0) 
### --------------------------------------------------------------------------------------
### Column 1 is East longitude (degrees)
### Columns 2+ are Water vapor column (kg/m2)
### Line 1 is North latitude (degrees)
### --------------------------------------------------------------------------------------
### Retrieved on: 2021-08-14T16:27:39.703997
### Mars Climate Database (c) LMD/OU/IAA/ESA/CNES
##########################################################################################"""
    data = data.split("\n")
    resp = parse_header(data)
    assert resp["mcd_version"] == "v5.3"
    assert resp["model"] == "climatology average solar scenario"
    assert resp["ls"] == "85.3deg"
    assert resp["altitude"] == "10.0 m"
    assert resp["local_time"] == "0.0h (at longitude 0)"
    assert resp["column_1"] == "East longitude (degrees)"
    assert resp["variable"] == "Water vapor column (kg/m2)"
    assert resp["keys"] == "North latitude (degrees)"
    assert resp["retrieval_date"] == datetime(2021, 8, 14, 16, 27, 39, 703997)
