# Coverage Tree — estructura por emisora y convención de nombres

## Workspace

```
workspace/
├── macro-view.yaml               # house view compartido (ver templates/macro-view.yaml)
└── <TICKER>/
    ├── profile/
    │   └── issuer-profile.yaml
    ├── filings/
    │   ├── sec/
    │   │   ├── 10-K/
    │   │   ├── 10-Q/
    │   │   └── 8-K/
    │   └── bmv/
    │       ├── annual/
    │       ├── quarterly/
    │       └── eventos-relevantes/
    ├── comps/                    # un comp-snapshot.yaml por comparable
    ├── model/
    │   └── <ticker>-model_YYYY-MM-DD_v#.xlsx
    ├── assumptions/
    │   └── driver-map.md
    ├── notes/
    │   ├── industry-report.md
    │   └── thesis-journal.md     # append-only
    └── log/
        ├── decisions.md          # observado / guidance / supuesto / output, con fecha
        └── forecast-accuracy.md  # calibración por driver entre trimestres
```

## Convención de nombres de filings

Formato: `<TICKER>_<tipo>_<periodo>[_fecha].<ext>` — pensado para retrieval, no para humanos.

| Documento | Nombre |
|---|---|
| 10-K FY2025 | `AMX_10-K_FY2025.pdf` |
| 10-Q 2T2026 | `AMX_10-Q_2Q2026.pdf` |
| 8-K | `AMX_8-K_2026-08-15.pdf` |
| Reporte anual BMV | `AMX_BMV-annual_FY2025.pdf` |
| Trimestral BMV | `AMX_BMV-quarterly_2Q2026.pdf` |
| Evento relevante | `AMX_evento-relevante_2026-08-15_<slug-corto>.pdf` |

Reglas:
- Ticker siempre en mayúsculas; periodos `FYyyyy` / `#Qyyyy`; fechas `YYYY-MM-DD`.
- Un archivo = un documento. Sin "final_v2_OK".
- **Nada se borra.** Filing reemplazado o corregido por la emisora: se archiva ambos, el
  nuevo con sufijo `_amended`. Retención mínima 7 años (Standard V(C)).
- Modelos: versionado `_YYYY-MM-DD_v#`; respaldo obligatorio antes de cada
  actualización trimestral (preflight de /update-quarter).
