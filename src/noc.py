"""NOC display and geo-mapping helpers.

NOC (IOC) codes do not always match ISO alpha-3 codes used by mapping libraries,
so we keep an explicit override table for the frequent divergences and for
historical delegations that have no modern ISO code.
"""

from __future__ import annotations

from functools import lru_cache

import pycountry


# Human-readable names, including historical delegations pycountry cannot resolve.
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
    "URS": "Soviet Union",
    "GDR": "East Germany",
    "FRG": "West Germany",
    "TCH": "Czechoslovakia",
    "YUG": "Yugoslavia",
    "SCG": "Serbia and Montenegro",
    "BOH": "Bohemia",
    "ANZ": "Australasia",
    "NED": "Netherlands",
    "SUI": "Switzerland",
    "GRE": "Greece",
    "DEN": "Denmark",
    "CRO": "Croatia",
    "POR": "Portugal",
}

# NOC (IOC) -> ISO alpha-3 for codes that differ from ISO. Used for choropleth maps.
NOC_TO_ISO3 = {
    "GER": "DEU", "NED": "NLD", "SUI": "CHE", "GRE": "GRC", "POR": "PRT",
    "DEN": "DNK", "CRO": "HRV", "SLO": "SVN", "BUL": "BGR", "LAT": "LVA",
    "INA": "IDN", "PHI": "PHL", "RSA": "ZAF", "ALG": "DZA", "MAS": "MYS",
    "KSA": "SAU", "UAE": "ARE", "IRI": "IRN", "TPE": "TWN", "KUW": "KWT",
    "CHI": "CHL", "URU": "URY", "PAR": "PRY", "PUR": "PRI", "ZIM": "ZWE",
    "ZAM": "ZMB", "MGL": "MNG", "VIE": "VNM", "SRI": "LKA", "NGR": "NGA",
    "NIG": "NER", "TAN": "TZA", "BAH": "BHS", "BRN": "BHR", "BAN": "BGD",
    "MYA": "MMR", "LIB": "LBN", "SUD": "SDN", "HAI": "HTI", "GUA": "GTM",
    "HON": "HND", "ESA": "SLV", "CRC": "CRI", "NCA": "NIC", "BIZ": "BLZ",
    "BOT": "BWA", "LES": "LSO", "MRI": "MUS", "SEY": "SYC", "MAD": "MDG",
    "GEO": "GEO", "TOG": "TGO", "MTN": "MRT", "GAM": "GMB", "GUI": "GIN",
    "ANG": "AGO", "MOZ": "MOZ", "CGO": "COG", "CHA": "TCD", "CAM": "KHM",
    "NEP": "NPL", "BHU": "BTN", "OMA": "OMN", "SYR": "SYR", "MRI": "MUS",
    "FIJ": "FJI", "PNG": "PNG", "VAN": "VUT", "SAM": "WSM", "TGA": "TON",
    "SOL": "SLB", "GRN": "GRD", "SKN": "KNA", "LCA": "LCA", "VIN": "VCT",
    "SUR": "SUR", "GUY": "GUY", "BAR": "BRB", "TRI": "TTO", "BER": "BMU",
    "ISV": "VIR", "IVB": "VGB", "CAY": "CYM", "ARU": "ABW", "BOL": "BOL",
    "ECU": "ECU", "PER": "PER", "MEX": "MEX",
    # Historical delegations without a modern ISO country -> intentionally omitted
    # (URS, GDR, FRG, TCH, YUG, SCG, EUN, ROC, ANZ, BOH) so they drop off the map.
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


@lru_cache(maxsize=512)
def noc_to_iso3(noc: str) -> str | None:
    """Map an NOC code to an ISO alpha-3 code for geographic charts.

    Returns None for historical delegations that have no modern ISO country.
    """
    if not isinstance(noc, str) or not noc.strip():
        return None
    key = noc.strip().upper()
    if key in NOC_TO_ISO3:
        return NOC_TO_ISO3[key]
    if pycountry.countries.get(alpha_3=key) is not None:
        return key
    return None


def format_noc_label(noc: str) -> str:
    return f"{noc} - {noc_to_country_name(noc)}"
