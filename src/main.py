import csv
import re
from argparse import ArgumentParser
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict


class TopLevel(Enum):
    ESSENTIAL = 1
    LIFESTYLE = 2
    IGNORE = 3


@dataclass
class Rule:
    top_level: TopLevel
    rule: re.Pattern = None
    category: str = ""
    detail: str = ""


DEFAULT_RULE = Rule(TopLevel.LIFESTYLE)


@dataclass
class Txn:
    date: str
    description: str
    amount: int
    rule: Rule

    def __repr__(self):
        return f"{self.date},{self.description},{self.amount},{self.rule.top_level.name},{self.rule.category},{self.rule.detail}"


class Rules:

    def __init__(self, rules_file: Path):
        self.rules = []

        with open(rules_file) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                self.rules.append(Rule(
                    TopLevel[row["top"].upper()],
                    re.compile(row['rule']),
                    row["category"],
                    row["detail"]
                ))

    def categorize(self, s) -> Rule:
        for rule in self.rules:
            if rule.rule.match(s):
                return rule

        return DEFAULT_RULE


def process_row(row: Dict[str, str], rules: Rules) -> Txn:
    return Txn(
        row.get("Transaction Date") or row["Posting Date"],
        row["Description"],
        int(float(row["Amount"])),
        rules.categorize(row["Description"])
    )


def run_categorize():
    parser = ArgumentParser()
    parser.add_argument("raw_file", help="input file with raw transaction data",
                        type=Path)
    parser.add_argument("--rules", help="file containing all the rules for labeling and categorization",
                        default="./rules.csv", type=Path)

    args = parser.parse_args()
    data = list(csv.DictReader(args.raw_file.open("r"), delimiter=","))
    rules = Rules(args.rules)
    for row in data:
        txn = process_row(row, rules)
        if txn.rule.top_level == TopLevel.IGNORE:
            continue
        print(txn)
