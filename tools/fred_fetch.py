"""FRED -> series macro historicas a macro/series/ (cadena macro del plugin).

Baja las series observadas (tasas, CPI, PIB, FX) para que la tab Macro del
modelo muestre HISTORICOS con fuente — no placeholders — y /update-macro
proponga macro-view.yaml desde datos, no desde memoria.

API key (gratuita, registro en https://fredaccount.stlouisfed.org/apikeys):
cascada --api-key -> env FRED_API_KEY -> macro/fred.key (decision del dueno
del plugin: archivo visible en el workspace) -> si falta, mensaje instruyendo
pegarla en el chat para que el agente la guarde en macro/fred.key.
La key JAMAS se imprime.

Uso:
    python tools/fred_fetch.py --dest <raiz>/macro/series
    python tools/fred_fetch.py --dest macro/series --series DGS10,DEXMXUS

Series extra: <raiz>/macro/fred-series.txt (un ID por linea; '#' comenta).
Consola ASCII-only.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Optional

API_URL = ("https://api.stlouisfed.org/fred/series/observations"
           "?series_id={sid}&api_key={key}&file_type=json")
META_URL = ("https://api.stlouisfed.org/fred/series"
            "?series_id={sid}&api_key={key}&file_type=json")

DEFAULT_SERIES = {
    "DGS10": "UST 10Y (riesgo libre USD)",
    "FEDFUNDS": "Fed Funds effective",
    "CPIAUCSL": "CPI US (indice)",
    "GDPC1": "PIB real US",
    "DEXMXUS": "USDMXN spot",
}

KEY_MSG = """[x] Falta la API key de FRED.
    Es GRATUITA: registrate en https://fredaccount.stlouisfed.org/apikeys
    (2 minutos, sin tarjeta). Luego, cualquiera de estas rutas:
    1) Pega la key en el chat y el agente la guarda en macro/fred.key.
    2) Crea el archivo macro/fred.key con la key como unico contenido.
    3) --api-key <key> o variable de entorno FRED_API_KEY."""

BLOCKED_MSG = """[x] Sin acceso de red a FRED ({err}).
    El entorno bloquea api.stlouisfed.org (proxy con allowlist — tipico en
    Claude Cowork). Opciones: 1) permitir api.stlouisfed.org en el allowlist
    del entorno; 2) correr este comando en una maquina con red y copiar
    macro/series/ al workspace."""


def _redact(text: str, key: str) -> str:
    return text.replace(key, "***") if key else text


def _get_json(url: str, key: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "research_analyst fred_fetch"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code in (403, 407):
            raise SystemExit(BLOCKED_MSG.format(err=f"HTTP {exc.code}"))
        if exc.code == 400:
            raise SystemExit("[x] FRED rechazo la solicitud (HTTP 400): "
                             "api key invalida o serie inexistente. Verifica "
                             "la key (macro/fred.key) y los IDs de serie.")
        raise SystemExit(_redact(f"[x] FRED HTTP {exc.code}: {exc.reason}", key))
    except urllib.error.URLError as exc:
        raise SystemExit(BLOCKED_MSG.format(err=str(exc.reason)))


def resolve_key(cli_key: Optional[str], dest: Path,
                key_file: Optional[str]) -> str:
    if cli_key:
        return cli_key.strip()
    env = os.environ.get("FRED_API_KEY", "").strip()
    if env:
        return env
    candidates = []
    if key_file:
        candidates.append(Path(key_file))
    candidates.append(dest.parent / "fred.key")   # macro/fred.key (dest=macro/series)
    candidates.append(dest / "fred.key")
    for path in candidates:
        try:
            content = path.read_text(encoding="utf-8").strip()
        except OSError:
            continue
        if content:
            return content.splitlines()[0].strip()
    raise SystemExit(KEY_MSG)


def series_list(dest: Path, cli_series: Optional[str]) -> dict[str, str]:
    if cli_series:
        return {s.strip().upper(): s.strip().upper()
                for s in cli_series.split(",") if s.strip()}
    out = dict(DEFAULT_SERIES)
    extra = dest.parent / "fred-series.txt"
    try:
        for line in extra.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                out.setdefault(line.upper(), line.upper())
    except OSError:
        pass
    return out


def fetch(dest: Path, key: str, wanted: dict[str, str]) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    manifest_rows = []
    for sid, title in wanted.items():
        data = _get_json(API_URL.format(sid=sid, key=key), key)
        obs = [(o["date"], o["value"]) for o in data.get("observations", [])
               if o.get("value") not in (".", "", None)]
        if not obs:
            print(f"[!] {sid}: sin observaciones — omitida")
            continue
        meta = _get_json(META_URL.format(sid=sid, key=key), key)
        info = (meta.get("seriess") or [{}])[0]
        out = dest / f"{sid}.csv"
        with out.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(["date", "value"])
            writer.writerows(obs)
        manifest_rows.append({
            "series": sid,
            "title": info.get("title", title),
            "units": info.get("units", ""),
            "frequency": info.get("frequency", ""),
            "last_observation": obs[-1][0],
            "last_value": obs[-1][1],
            "source": "FRED (Federal Reserve Bank of St. Louis)",
            "tag": "observado",
        })
        print(f"[ok] {sid}: {len(obs)} observaciones "
              f"({obs[0][0]} .. {obs[-1][0]}) -> {out.name}")
    if manifest_rows:
        mpath = dest / "manifest.csv"
        with mpath.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(manifest_rows[0].keys()))
            writer.writeheader()
            writer.writerows(manifest_rows)
        print(f"[ok] manifest: {mpath}")
    print("[i] siguiente paso: /update-macro propone macro-view.yaml desde")
    print("    estas series (gate por campo); la tab Macro del modelo las lee.")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="FRED -> macro/series/*.csv")
    parser.add_argument("--dest", default="macro/series",
                        help="carpeta destino (default: macro/series)")
    parser.add_argument("--api-key", default=None, help="key FRED (o env/archivo)")
    parser.add_argument("--key-file", default=None,
                        help="ruta a archivo con la key (default: macro/fred.key)")
    parser.add_argument("--series", default=None,
                        help="IDs separados por coma (default: set estandar + fred-series.txt)")
    args = parser.parse_args(argv[1:])
    dest = Path(args.dest)
    key = resolve_key(args.api_key, dest, args.key_file)
    fetch(dest, key, series_list(dest, args.series))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
