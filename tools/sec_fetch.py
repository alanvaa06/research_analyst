"""SEC EDGAR filing downloader for the research_analyst plugin.

Deterministic fetch step for /init-coverage and /update-quarter: when the
coverage folders lack filings for an SEC issuer, this tool downloads them from
EDGAR (free, public). It downloads RAW primary documents named by report date;
renaming to the coverage-tree convention (FYyyyy / #Qyyyy) is coverage-folders'
job — that skill owns naming, this tool only fetches.

SEC fair-access rules: a User-Agent identifying the requester is REQUIRED
(name + email). Pass it with --ua or the SEC_EDGAR_UA env var; it is never
hardcoded (public repo). Requests are throttled to ~4/s.

Usage:
    python tools/sec_fetch.py AAPL --dest workspace/AAPL/filings/sec \
        --ua "Nombre Apellido correo@dominio.com"
    python tools/sec_fetch.py AAPL --forms 10-K,10-Q --since 2020-01-01 --dry-run

Console output: ASCII only.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

SEC_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
SEC_SUBMISSIONS_URL = "https://data.sec.gov/submissions/{name}"
SEC_ARCHIVES_URL = "https://www.sec.gov/Archives/edgar/data/{cik}/{accn}/{doc}"
SEC_FOLDER_INDEX_URL = "https://www.sec.gov/Archives/edgar/data/{cik}/{accn}/index.json"

# Files never worth downloading from a filing folder (graphics, XBRL plumbing).
_EXHIBIT_SKIP_SUFFIXES = (".jpg", ".jpeg", ".gif", ".png", ".xml", ".xsd",
                          ".css", ".js", ".json", ".txt", ".zip", ".paper")

DEFAULT_FORMS = ("10-K", "10-Q", "8-K")
DEFAULT_SINCE = "2016-01-01"
THROTTLE_SECONDS = 0.25


@dataclass(frozen=True)
class FilingRow:
    """One EDGAR filing entry (metadata only)."""

    form: str
    filed: str
    period: str
    accession: str
    primary_doc: str


BLOCKED_MSG = """[x] Sin acceso de red a SEC ({err}).
    El entorno bloquea www.sec.gov / data.sec.gov (proxy con allowlist —
    tipico en Claude Cowork y sandboxes corporativos). Opciones:
    1) Permitir los dominios www.sec.gov y data.sec.gov en el entorno
       (Cowork: configuracion de red/allowlist del espacio) y reintentar.
    2) Correr este mismo comando en una maquina con salida a internet y
       copiar los archivos resultantes a la carpeta destino.
    3) Descargar los filings a mano desde efts.sec.gov/LATEST/search-index
       y dejar que coverage-folders los archive.
    NUNCA sustituyas el filing integro por contenido procesado de un lector
    web: el pipeline cita por documento y pagina."""


def _get_json(url: str, user_agent: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": user_agent})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (urllib.error.HTTPError, urllib.error.URLError) as exc:
        code = getattr(exc, "code", None)
        if code in (403, 407) or isinstance(exc, urllib.error.URLError):
            raise SystemExit(BLOCKED_MSG.format(err=f"{type(exc).__name__} {code or exc.reason}"))
        raise


def _download(url: str, dest: Path, user_agent: str) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": user_agent})
    with urllib.request.urlopen(req, timeout=120) as resp:
        dest.write_bytes(resp.read())


def resolve_cik(ticker: str, user_agent: str) -> str:
    """Ticker -> zero-padded 10-digit CIK via SEC's public mapping."""
    data = _get_json(SEC_TICKERS_URL, user_agent)
    wanted = ticker.upper()
    for entry in data.values():
        if str(entry.get("ticker", "")).upper() == wanted:
            return f"{int(entry['cik_str']):010d}"
    raise SystemExit(f"[x] ticker {wanted} no encontrado en SEC company_tickers.json")


def list_filings(cik10: str, forms: Iterable[str], since: str,
                 user_agent: str) -> list[FilingRow]:
    """All matching filings, oldest first, across the paged submission files."""
    wanted = {f.upper() for f in forms}
    root = _get_json(SEC_SUBMISSIONS_URL.format(name=f"CIK{cik10}.json"), user_agent)
    batches = [root["filings"]["recent"]]
    for extra in root["filings"].get("files", []):
        time.sleep(THROTTLE_SECONDS)
        batches.append(_get_json(SEC_SUBMISSIONS_URL.format(name=extra["name"]),
                                 user_agent))
    rows: list[FilingRow] = []
    for batch in batches:
        for i in range(len(batch["form"])):
            form = batch["form"][i]
            filed = batch["filingDate"][i]
            if form.upper() in wanted and filed >= since:
                rows.append(FilingRow(
                    form=form,
                    filed=filed,
                    period=batch["reportDate"][i] or filed,
                    accession=batch["accessionNumber"][i],
                    primary_doc=batch["primaryDocument"][i],
                ))
    return sorted(rows, key=lambda r: r.filed)


def list_8k_exhibits(cik_short: str, accn_flat: str, primary_doc: str,
                     user_agent: str) -> list[str]:
    """Exhibit documents of one 8-K folder (press release EX-99.* lives here).

    Deterministic filter over the accession's index.json: every .htm that is
    not the primary wrapper nor an index page. 8-K folders are small (wrapper +
    1-2 exhibits + plumbing), so this stays precise without HTML parsing.
    """
    url = SEC_FOLDER_INDEX_URL.format(cik=cik_short, accn=accn_flat)
    data = _get_json(url, user_agent)
    items = data.get("directory", {}).get("item", [])
    import re
    exhibits: list[str] = []
    primary_lower = primary_doc.lower()
    for item in items:
        name = str(item.get("name", ""))
        low = name.lower()
        if not low.endswith(".htm") and not low.endswith(".html"):
            continue
        if low == primary_lower or "index" in low:
            continue
        if re.fullmatch(r"r\d+\.htm", low):  # XBRL viewer artifact, not a doc
            continue
        if low.endswith(_EXHIBIT_SKIP_SUFFIXES):
            continue
        exhibits.append(name)
    return exhibits


def fetch(ticker: str, dest: Path, forms: Iterable[str], since: str,
          user_agent: str, dry_run: bool = False) -> Path:
    """Download filings + write manifest CSV. Returns the manifest path."""
    cik10 = resolve_cik(ticker, user_agent)
    cik_short = str(int(cik10))
    rows = list_filings(cik10, forms, since, user_agent)
    print(f"[ok] {ticker.upper()} CIK {cik10}: {len(rows)} filings "
          f"({','.join(forms)} desde {since})")
    dest.mkdir(parents=True, exist_ok=True)
    manifest_rows: list[dict[str, str]] = []
    for row in rows:
        accn_flat = row.accession.replace("-", "")
        url = SEC_ARCHIVES_URL.format(cik=cik_short, accn=accn_flat,
                                      doc=row.primary_doc)
        ext = Path(row.primary_doc).suffix or ".htm"
        # Raw name by report date; coverage-folders renames to FY/#Q convention.
        name = f"{ticker.upper()}_{row.form}_{row.period}{ext}"
        path = dest / name
        if dry_run:
            print(f"[dry] {name}  <-  {url}")
        elif path.exists():
            print(f"[ok] ya existe: {name}")
        else:
            print(f"[..] bajando: {name}")
            _download(url, path, user_agent)
            time.sleep(THROTTLE_SECONDS)
        manifest_rows.append({
            "file": name, "form": row.form, "filed": row.filed,
            "period": row.period, "accession": row.accession, "source": url,
        })
        # 8-K: also fetch exhibits — EX-99.* press release carries the
        # quarter's quantitative guidance (transcripts do NOT live on EDGAR).
        if row.form.upper().startswith("8-K"):
            time.sleep(THROTTLE_SECONDS)
            try:
                exhibits = list_8k_exhibits(cik_short, accn_flat,
                                            row.primary_doc, user_agent)
            except Exception as exc:  # noqa: BLE001 - red flaky, filing sigue
                print(f"[!] exhibits no listados para {row.accession}: {exc}")
                exhibits = []
            for ex_doc in exhibits:
                ex_url = SEC_ARCHIVES_URL.format(cik=cik_short, accn=accn_flat,
                                                 doc=ex_doc)
                ex_name = f"{ticker.upper()}_{row.form}_{row.period}_ex_{Path(ex_doc).name}"
                ex_path = dest / ex_name
                if dry_run:
                    print(f"[dry] {ex_name}  <-  {ex_url}")
                elif ex_path.exists():
                    print(f"[ok] ya existe: {ex_name}")
                else:
                    print(f"[..] bajando exhibit: {ex_name}")
                    _download(ex_url, ex_path, user_agent)
                    time.sleep(THROTTLE_SECONDS)
                manifest_rows.append({
                    "file": ex_name, "form": f"{row.form}-EX", "filed": row.filed,
                    "period": row.period, "accession": row.accession,
                    "source": ex_url,
                })
    manifest = dest / f"{ticker.upper()}_filings_manifest.csv"
    if not dry_run:
        with manifest.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(manifest_rows[0].keys())
                                    if manifest_rows else ["file"])
            writer.writeheader()
            writer.writerows(manifest_rows)
        print(f"[ok] manifest: {manifest}")
    return manifest


def _resolve_user_agent(cli_value: Optional[str]) -> str:
    ua = cli_value or os.environ.get("SEC_EDGAR_UA", "")
    if not ua or "@" not in ua:
        raise SystemExit(
            "[x] SEC exige User-Agent con contacto (nombre + email).\n"
            "    Pasa --ua \"Nombre correo@dominio.com\" o define SEC_EDGAR_UA.")
    return ua


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Descarga filings SEC EDGAR")
    parser.add_argument("ticker")
    parser.add_argument("--forms", default=",".join(DEFAULT_FORMS),
                        help="lista separada por comas (default: 10-K,10-Q,8-K)")
    parser.add_argument("--since", default=DEFAULT_SINCE, help="YYYY-MM-DD")
    parser.add_argument("--dest", default=".", help="carpeta destino")
    parser.add_argument("--ua", default=None,
                        help="User-Agent 'Nombre correo' (o env SEC_EDGAR_UA)")
    parser.add_argument("--dry-run", action="store_true",
                        help="listar sin descargar")
    args = parser.parse_args(argv[1:])
    user_agent = _resolve_user_agent(args.ua)
    forms = [f.strip() for f in args.forms.split(",") if f.strip()]
    fetch(args.ticker, Path(args.dest), forms, args.since, user_agent,
          dry_run=args.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
