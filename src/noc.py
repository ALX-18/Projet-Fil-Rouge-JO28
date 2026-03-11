"""NOC display helpers."""

from __future__ import annotations

from functools import lru_cache

import pycountry


OVERRIDES = {
    "USA": "United States",
    "FRA": "France",
    "GBR": "United Kingdom",
    "GER": "Germany",
    "CHN": "China",
    "JPN": "Japan",
    "KOR": "South Korea",
    "ROC": "Russian Olympic Committee",
    "EUN": "Unified Team",
}


@lru_cache(maxsize=512)
def noc_to_country_name(noc: str) -> str:
    if not isinstance(noc, str) or not noc.strip():
        return "Unknown"
    key = noc.strip().upper()
    if key in OVERRIDES:
        return OVERRIDES[key]

    country = pycountry.countries.get(alpha_3=key)
    if country is not None:
        return country.name
    return key


def format_noc_label(noc: str) -> str:
    return f"{noc} - {noc_to_country_name(noc)}"
