import csv
import re
from argparse import ArgumentParser
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class TopLevel(Enum):
    ESSENTIAL = 1
    LIFESTYLE = 2


@dataclass
class Txn:
    date: str
    description: str
    amount: int
    top_level: TopLevel
    category: str
    detail: str

    def __repr__(self):
        return f"{self.date},{self.description},{self.amount},{self.top_level},{self.category},{self.detail}"


ESSENTIALS_RULES = {
    r"^.*ATT\*BILL PAYMENT.*$": ("bills", "phone"),
    r"^.*CHEWY.COM.*$": ("Daisy", ""),
    r"^.*COMCAST.*$": ("Bills", "Internet"),
    r"^.*COMED.*$": ("Bills", "Utilities"),
    r"^.*COSTCO.*$": ("Food", "Grocery Store"),
    r"^.*FREETAXUSA.COM.*$": ("Bills", "Taxes"),
    r"^.*GEICO.*$": ("Insurance", "Car"),
    r"^.*HUNTINGTON BANKS.*$": ("Car", "Car Payment"),
    r"^.*IRS  USATAXPYMT.*$": ("Bills", "Taxes"),
    r"^.*JET BRITE.*$": ("Car", "Improvement"),
    r"^.*JEWEL OSCO \d+.*$": ("Food", "Grocery Store"),
    r"^.*KRISERS NAT PET.*$": ("Daisy", ""),
    r"^.*LIBERTY MUTUAL.*$": ("House", "Insurance"),
    r"^.*LOMBARD DIST 44 LUNCH PRO.*$": ("Food", ""),
    r"^.*LOMBARD GAS STATION.*$": ("Car", "Gas"),
    r"^.*LOMBARD VETERINARY.*$": ("Daisy", ""),
    r"^.*MARIANOS.*$": ("Food", "Grocery Store"),
    r"^.*Morgan Stanley   ACH DEBIT.*$": ("Investment", ""),
    r"^.*NICOR GAS BILL.*$": ("Bills", "Utilities"),
    r"^.*Oberweis.*$": ("Food", "Specialty"),
    r"^.*PAYPAL \*VILLAGELOMB.*$": ("Bills", "Utilities"),
    r"^.*SHELL OIL.*$": ("Car", "Gas"),
    r"^.*TRUIST.*$": ("House", "Mortgage"),
    r"^.*WASTE MANAGEMENT INTERNET.*$": ("Bills", "Utilities"),
}

LIFESTYLE_RULES = {
    r"^Subway \d+$": ("food", "family"),
}


class Rules:

    def __init__(self):
        self.essentials = {re.compile(k): v for k, v in ESSENTIALS_RULES.items()}
        self.lifestyle = {re.compile(k): v for k, v in LIFESTYLE_RULES.items()}

    def categorize(self, s):
        for pat, (category, detail) in self.essentials.items():
            if pat.match(s):
                return TopLevel.ESSENTIAL, category, detail

        for pat, (category, detail) in self.lifestyle.items():
            if pat.match(s):
                return TopLevel.LIFESTYLE, category, detail

        return TopLevel.LIFESTYLE, "", ""


def process_row(row: dict[str, str], rules) -> Txn:
    return Txn(
        row["Transaction Date"],
        row["Description"],
        int(float(row["Amount"])),
        *rules.categorize(row["Description"])
    )


def run_categorize():
    parser = ArgumentParser()
    parser.add_argument("raw_file", help="input file with raw transaction data",
                        type=Path)

    args = parser.parse_args()
    data = list(csv.DictReader(args.raw_file.open("r"), delimiter=","))
    rules = Rules()
    for row in data:
        txn = process_row(row, rules)
        print(txn)
