# /// script
# dependencies = [
#    "beautifulsoup4>=4.14.2",
#    "lxml>=6.0.2",
#    "requests>=2.32.5",
# ]
# ///

import json
import pathlib
from typing import TypedDict

import bs4
import requests

URL = "https://phasmophobia.fandom.com/wiki/Experience"
RESOURCE_FILE = pathlib.Path(__file__).parent.parent / "resources" / "levelscaling.json"


class Scale(TypedDict):
    to_next: int
    cumulative: int


def get_soup() -> bs4.BeautifulSoup:
    data = requests.get(URL, timeout=5.0)
    data.raise_for_status()

    return bs4.BeautifulSoup(data.text, features="lxml")


skip_ = {0, 1, -2, -4}


def parse(soup: bs4.BeautifulSoup) -> dict[int, Scale]:
    ret: dict[int, Scale] = {}
    table = soup.find("table", class_="mw-collapsible mw-collapsed fandom-table")
    if not table:
        raise RuntimeError("Unable to get table data from url.")

    table_body = table.select("tbody")
    if not table_body:
        raise RuntimeError("Got an unknown result for table and table body.")
    body = table_body[0]

    rows = body.find_all("tr")
    for idx, row in enumerate(rows):
        if idx in skip_ or idx == len(rows) + (-2) or idx == len(rows) + (-4):
            continue

        useful = row.find_all("td")[:3]
        level_, xp_, cum_xp_ = useful
        level, xp, cum_xp = (
            int(level_.text.strip().replace(",", "")),
            int(xp_.text.strip().replace(",", "").replace("-", "0")),
            int(cum_xp_.text.strip().replace(",", "")),
        )
        ret[level] = {"to_next": xp, "cumulative": cum_xp}

    return dict(sorted(ret.items()))


if __name__ == "__main__":
    soup = get_soup()
    scaling = parse(soup)
    with RESOURCE_FILE.open("w", encoding="utf-8") as fp:
        json.dump(scaling, fp, indent=2)
