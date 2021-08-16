import csv
import pytest
from pathlib import Path
from devtools import debug
from typing import List, Union
from datetime import datetime
from collections import namedtuple
import numpy as np
import re


def parse_number(num: str) -> Union[float, int]:
    if num == "----":
        return None
    try:
        return int(num)
    except ValueError:
        return float(num)


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


DataTable = namedtuple("DataTable", ["data", "xlabels", "ylabels"])


def parse_body(body: List[str]) -> "DataTable":
    # here we use the map (/reduce, but here we don't reduce) paradigm to show how sometimes functional programming is a *lot* simpler than writing the loops out by hand.
    # map applies a function (here an anonymous function decared with lambda) over an iterable
    # numpy has it's own map/reduce fns which are implemented in C and can be a lot faster than python's.
    body = map(lambda row: " ".join(row.strip().split()), body)
    body = list(body)
    xlabels = body[0].split("||")[1].strip().split(" ")
    body = body[2:]
    xlabels = map(lambda x: parse_number(x), xlabels)
    ylabels = map(lambda row: row.split("||")[0].strip(), body)
    ylabels = map(lambda x: parse_number(x), ylabels)
    data = map(lambda row: row.split("||")[1].strip().split(" "), body)
    data = np.array(list(data))
    data = DataTable(data, list(xlabels), list(ylabels))
    return data


def read_ascii_data(dataf):
    sections = {}
    with dataf.open() as f:
        row = f.readline()
        while True:
            if not row:
                break
            while "#" * 8 not in row:  # start header section
                row = f.readline()
            header = []
            for row in f.read():  # starts at line after last read
                if "#" * 8 in row:  # start header section
                    break
                header.append(row)
            header = parse_header(header)

            # parse body
            body = []
            row = f.readline()
            while "#" * 8 not in row:  # start header section
                body.append(row)
                row = f.readline()
            body = parse_body(body)

            sections[header["keys"]] = body
    return sections


# inf = Path("~/Downloads/data.txt").expanduser()
# read_ascii_data(inf)


def test_parse_body():
    body = """---- ||   -9.00000e+01   -8.61702e+01   -8.23404e+01   -7.85106e+01   -7.46809e+01   -7.08511e+01   -6.70213e+01   -6.31915e+01   -5.93617e+01   -5.55319e+01   -5.17021e+01   -4.78723e+01   -4.40426e+01   -4.02128e+01   -3.63830e+01   -3.25532e+01   -2.87234e+01   -2.48936e+01   -2.10638e+01   -1.72340e+01   -1.34043e+01   -9.57447e+00   -5.74468e+00   -1.91489e+00    1.91489e+00    5.74468e+00    9.57447e+00    1.34043e+01    1.72340e+01    2.10638e+01    2.48936e+01    2.87234e+01    3.25532e+01    3.63830e+01    4.02128e+01    4.40426e+01    4.78723e+01    5.17021e+01    5.55319e+01    5.93617e+01    6.31915e+01    6.70213e+01    7.08511e+01    7.46809e+01    7.85106e+01    8.23404e+01    8.61702e+01    9.00000e+01
-----------------------------------
-180 ||    3.85941e-07    3.54776e-07    3.12143e-07    3.26378e-07    4.40781e-07    6.51328e-07    9.64859e-07    1.58060e-06    3.46786e-06    1.03584e-05    3.59026e-05    1.14634e-04    3.10848e-04    6.85023e-04    1.28657e-03    1.96361e-03    2.84410e-03    3.58751e-03    3.96411e-03    4.58151e-03    6.70365e-03    7.33091e-03    8.40377e-03    1.01448e-02    1.17229e-02    1.28424e-02    1.37919e-02    1.40092e-02    1.55745e-02    1.68401e-02    1.80063e-02    2.04580e-02    2.46005e-02    2.97717e-02    3.41619e-02    3.71240e-02    3.91904e-02    4.19624e-02    4.46246e-02    4.73612e-02    5.17239e-02    5.51091e-02    5.86257e-02    6.15134e-02    6.02517e-02    4.47480e-02    2.85537e-02    1.91096e-02"""
    body = body.split("\n")
    resp = parse_body(body)
    xlabels = [
        -9.00000e01,
        -8.61702e01,
        -8.23404e01,
        -7.85106e01,
        -7.46809e01,
        -7.08511e01,
        -6.70213e01,
        -6.31915e01,
        -5.93617e01,
        -5.55319e01,
        -5.17021e01,
        -4.78723e01,
        -4.40426e01,
        -4.02128e01,
        -3.63830e01,
        -3.25532e01,
        -2.87234e01,
        -2.48936e01,
        -2.10638e01,
        -1.72340e01,
        -1.34043e01,
        -9.57447e00,
        -5.74468e00,
        -1.91489e00,
        1.91489e00,
        5.74468e00,
        9.57447e00,
        1.34043e01,
        1.72340e01,
        2.10638e01,
        2.48936e01,
        2.87234e01,
        3.25532e01,
        3.63830e01,
        4.02128e01,
        4.40426e01,
        4.78723e01,
        5.17021e01,
        5.55319e01,
        5.93617e01,
        6.31915e01,
        6.70213e01,
        7.08511e01,
        7.46809e01,
        7.85106e01,
        8.23404e01,
        8.61702e01,
        9.00000e01,
    ]
    data = np.array(
        [
            [
                "3.85941e-07",
                "3.54776e-07",
                "3.12143e-07",
                "3.26378e-07",
                "4.40781e-07",
                "6.51328e-07",
                "9.64859e-07",
                "1.58060e-06",
                "3.46786e-06",
                "1.03584e-05",
                "3.59026e-05",
                "1.14634e-04",
                "3.10848e-04",
                "6.85023e-04",
                "1.28657e-03",
                "1.96361e-03",
                "2.84410e-03",
                "3.58751e-03",
                "3.96411e-03",
                "4.58151e-03",
                "6.70365e-03",
                "7.33091e-03",
                "8.40377e-03",
                "1.01448e-02",
                "1.17229e-02",
                "1.28424e-02",
                "1.37919e-02",
                "1.40092e-02",
                "1.55745e-02",
                "1.68401e-02",
                "1.80063e-02",
                "2.04580e-02",
                "2.46005e-02",
                "2.97717e-02",
                "3.41619e-02",
                "3.71240e-02",
                "3.91904e-02",
                "4.19624e-02",
                "4.46246e-02",
                "4.73612e-02",
                "5.17239e-02",
                "5.51091e-02",
                "5.86257e-02",
                "6.15134e-02",
                "6.02517e-02",
                "4.47480e-02",
                "2.85537e-02",
                "1.91096e-02",
            ]
        ],
        dtype="<U11",
    )
    assert len(resp.xlabels) == len(xlabels)
    assert resp.xlabels == pytest.approx(xlabels)
    assert resp.ylabels == [-180]
    assert (resp.data == data).all()


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
