import csv
from argparse import ArgumentParser
from dataclasses import dataclass
from pathlib import Path
import re
from typing import Tuple


@dataclass
class Txn:
    date: str
    description: str
    amount: int
    tag_1: str
    tag_2: str

    def __repr__(self):
        return f"{self.date},{self.description},{self.amount},{self.tag_1},{self.tag_2}"


RULES = {
    re.compile(r"^Subway \d+$"): ("food", "family")
}


def categorize(description: str) -> Tuple[str, str]:
    for pat, tags in RULES.items():
        if pat.match(description):
            return tags
    return "", ""


def process_row(row: dict[str, str]) -> Txn:
    return Txn(
        row["Transaction Date"],
        row["Description"],
        int(float(row["Amount"])),
        *categorize(row["Description"])
    )


def run_categorize():
    parser = ArgumentParser()
    parser.add_argument("raw_file", help="input file with raw transaction data",
                        type=Path)

    args = parser.parse_args()
    data = list(csv.DictReader(args.raw_file.open("r"), delimiter=","))
    for row in data:
        txn = process_row(row)
        print(txn)
