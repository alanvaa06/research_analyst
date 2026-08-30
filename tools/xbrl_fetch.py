"""SEC XBRL companyfacts -> serie historica completa (anual + trimestral).

Resuelve la captura masiva de trimestres sin parsear HTML: la API publica
``data.sec.gov/api/xbrl/companyfacts`` trae TODOS los valores reportados de la
emisora (10-K y 10-Q, con periodo fiscal fp/fy). Este tool baja los conceptos
US GAAP mapeados a lineas canon y escribe un CSV largo que statement-mapper
convierte (con gate) en los canonical_*.csv de model/inputs/.

Uso:
    python tools/xbrl_fetch.py AAPL --dest workspace/AAPL/model/inputs \
        --ua "Nombre correo@dominio.com"

User-Agent obligatorio (--ua o env SEC_EDGAR_UA), igual que sec_fetch.
Consola ASCII-only.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import urllib.request
from pathlib import Path
from typing import Optional

FACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"

# Concepto US GAAP -> linea canon. Lista ampliable; un concepto ausente en la
# emisora simplemente no emite filas (se reporta al final).
CONCEPT_MAP = {
    "RevenueFromContractWithCustomerExcludingAssessedTax": "is_ns_total",
    "Revenues": "is_ns_total_alt",
    "CostOfGoodsAndServicesSold": "is_cogs_total",
    "GrossProfit": "is_gross",
    "ResearchAndDevelopmentExpense": "is_rd",
    "SellingGeneralAndAdministrativeExpense": "is_sga",
    "OperatingIncomeLoss": "is_ebit",
    "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest": "is_ebt",
    "IncomeTaxExpenseBenefit": "is_tax",
    "NetIncomeLoss": "is_ni",
    "EarningsPerShareDiluted": "is_eps_diluted",
    "Assets": "bs_ta",
    "AssetsCurrent": "bs_ca",
    "LiabilitiesCurrent": "bs_cl",
    "Liabilities": "bs_tl",
    "StockholdersEquity": "bs_equity",
    "CashAndCashEquivalentsAtCarryingValue": "bs_cash",
    "InventoryNet": "bs_inv",
    "AccountsReceivableNetCurrent": "bs_ar",
    "AccountsPayableCurrent": "bs_ap",
    "RetainedEarningsAccumulatedDeficit": "bs_re",
    "LongTermDebtNoncurrent": "bs_debt_lt",
    "LongTermDebtCurrent": "bs_debt_st",
    "CommercialPaper": "bs_commercial_paper",
    "NetCashProvidedByUsedInOperatingActivities": "cf_cfo",
    "DepreciationDepletionAndAmortization": "cf_da",
    "PaymentsToAcquirePropertyPlantAndEquipment": "cf_capex",
    "PaymentsForRepurchaseOfCommonStock": "cf_buybacks",
    "PaymentsOfDividends": "cf_dividends",
}


def _get_json(url: str, user_agent: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": user_agent})
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode("utf-8"))


def resolve_cik(ticker: str, user_agent: str) -> str:
    data = _get_json(TICKERS_URL, user_agent)
    wanted = ticker.upper()
    for entry in data.values():
        if str(entry.get("ticker", "")).upper() == wanted:
            return f"{int(entry['cik_str']):010d}"
    raise SystemExit(f"[x] ticker {wanted} no encontrado")


def period_label(item: dict) -> Optional[str]:
    """fp/fy de SEC ya son FISCALES: Q1/FY2026 -> 1Q2026 / FY2026."""
    fp = item.get("fp")
    fy = item.get("fy")
    if not fp or not fy:
        return None
    if fp == "FY":
        return f"FY{fy}"
    if fp in ("Q1", "Q2", "Q3", "Q4"):
        return f"{fp[1]}Q{fy}"
    return None


def fetch(ticker: str, dest: Path, user_agent: str) -> Path:
    cik = resolve_cik(ticker, user_agent)
    data = _get_json(FACTS_URL.format(cik=cik), user_agent)
    facts = data.get("facts", {}).get("us-gaap", {})
    rows: dict[tuple[str, str], dict] = {}
    found: set[str] = set()
    for concept, canon in CONCEPT_MAP.items():
        node = facts.get(concept)
        if not node:
            continue
        found.add(concept)
        for unit, items in node.get("units", {}).items():
            if unit not in ("USD", "USD/shares"):
                continue
            for item in items:
                label = period_label(item)
                if not label:
                    continue
                key = (canon, label)
                prev = rows.get(key)
                # dedup: gana el filed mas reciente (re-presentaciones)
                if prev is None or item.get("filed", "") > prev["filed"]:
                    rows[key] = {
                        "canon": canon, "period": label,
                        "value": item.get("val"),
                        "start": item.get("start", ""), "end": item.get("end", ""),
                        "form": item.get("form", ""), "filed": item.get("filed", ""),
                        "concept": concept, "unit": unit,
                        "source": f"XBRL companyfacts CIK{cik} {concept}",
                        "tag": "observado",
                    }
    dest.mkdir(parents=True, exist_ok=True)
    out = dest / f"xbrl_facts_{ticker.upper()}.csv"
    fieldnames = ["canon", "period", "value", "start", "end", "form", "filed",
                  "concept", "unit", "source", "tag"]
    ordered = sorted(rows.values(), key=lambda r: (r["canon"], r["end"]))
    with out.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(ordered)
    quarters = sorted({r["period"] for r in ordered if "Q" in r["period"]})
    years = sorted({r["period"] for r in ordered if r["period"].startswith("FY")})
    print(f"[ok] {ticker.upper()}: {len(ordered)} observaciones -> {out.name}")
    print(f"[ok] trimestres cubiertos: {len(quarters)} ({quarters[0] if quarters else '-'}"
          f" .. {quarters[-1] if quarters else '-'})")
    print(f"[ok] anios cubiertos: {len(years)}")
    missing = sorted(set(CONCEPT_MAP) - found)
    if missing:
        print(f"[!] conceptos sin datos en esta emisora ({len(missing)}): "
              + ", ".join(missing[:6]) + (" ..." if len(missing) > 6 else ""))
    print("[i] siguiente paso: statement-mapper convierte este CSV largo en los")
    print("    canonical_*.csv (mapeo canon con gate del analista); 4Q de flujos")
    print("    se deriva FY - (1Q+2Q+3Q).")
    return out


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="SEC XBRL companyfacts -> CSV largo")
    parser.add_argument("ticker")
    parser.add_argument("--dest", default=".", help="carpeta destino (model/inputs)")
    parser.add_argument("--ua", default=None, help="User-Agent 'Nombre correo' (o env SEC_EDGAR_UA)")
    args = parser.parse_args(argv[1:])
    ua = args.ua or os.environ.get("SEC_EDGAR_UA", "")
    if not ua or "@" not in ua:
        raise SystemExit("[x] SEC exige User-Agent con contacto: --ua o env SEC_EDGAR_UA")
    fetch(args.ticker, Path(args.dest), ua)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
