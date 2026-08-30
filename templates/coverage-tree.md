# Coverage Tree — estructura por emisora y convención de nombres

## Workspace

Cuatro categorías: **inputs** (lo que entra) / **config** / **outputs** (lo que
el pipeline produce) / **registro** (memoria append-only). Archivos-contrato
únicos viven en la RAÍZ del ticker — un archivo no gana carpeta.

```
workspace/
├── macro-view.yaml               # house view compartido — SOLO aquí; instanciarlo
│                                 # dentro de un ticker es violación de contrato
└── <TICKER>/
    ├── issuer-profile.yaml       # contrato raíz (framework-mapper)
    ├── driver-map.md             # contrato raíz (driver-inventory)
    ├── filings/                  # INPUTS
    │   ├── sec/
    │   │   ├── 10-K/
    │   │   ├── 10-Q/
    │   │   └── 8-K/
    │   └── bmv/
    │       ├── annual/
    │       ├── quarterly/
    │       └── eventos-relevantes/
    ├── transcripts/              # INPUTS: earnings calls — si están, SE CONSIDERAN
    │                             # (statement-mapper los lee como fuente de guidance)
    ├── comps/                    # INPUTS: un comp-snapshot.yaml por comparable
    ├── brand/                    # CONFIG
    │   └── DESIGN.md             # opcional: colores de marca del analista (slots abajo)
    ├── model/                    # OUTPUTS
    │   ├── <ticker>-model_YYYY-MM-DD_v#.xlsx
    │   └── inputs/               # capa de captura (statement-mapper escribe,
    │       │                     #   model-standards consume; viaja con el modelo)
    │       ├── canonical_annual.csv      # CONTRATO: series anuales observadas
    │       ├── canonical_quarterly.csv   # CONTRATO: series trimestrales observadas
    │       ├── consolidated_long.csv     # CONTRATO: formato tidy largo (todas)
    │       └── extract_*.json            # papeles de trabajo por filing, con citas
    ├── research/                 # OUTPUTS: análisis
    │   └── industry-report.md    #   (+ notas y reportes futuros)
    └── journal/                  # REGISTRO append-only
        ├── thesis-journal.md     # entradas de cada gate/debate
        ├── decisions.md          # observado / guidance / supuesto / output, con fecha
        └── forecast-accuracy.md  # calibración por driver entre trimestres
```

### model/inputs/ — la capa de captura

Los CSV canónicos son el CONTRATO máquina entre statement-mapper y
model-standards; los `extract_*.json` son papeles de trabajo (citas por cifra:
documento, página/nota, fecha). Columnas mínimas de los CSV: `line_item`,
`period`, `value`, `source_doc`, `source_ref`, `tag` (observado/guidance).
El histórico del xlsx se puebla DESDE los canónicos — check C9 verifica que
coincidan. Regenerables desde los JSON; los JSON, desde los filings. Nada se
teclea dos veces.

### Migración desde el árbol v1 (coberturas existentes)

Solo movimientos, nada se borra (Standard V(C)):
`profile/issuer-profile.yaml` → raíz · `assumptions/driver-map.md` → raíz ·
`notes/industry-report.md` → `research/` · `notes/thesis-journal.md` →
`journal/` · `log/*` → `journal/` · `earnings-transcripts/` → `transcripts/` ·
`macro-view.yaml` dentro del ticker → subirlo al workspace (si ya existe uno en
workspace, preguntar cuál manda — nunca resolver en silencio). Carpetas viejas
vacías se eliminan al final (carpeta vacía no es dato).

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
| Transcript de earnings call | `AMX_transcript_2Q2026.pdf` |

Reglas:
- Ticker siempre en mayúsculas; periodos `FYyyyy` / `#Qyyyy`; fechas `YYYY-MM-DD`.
- Un archivo = un documento. Sin "final_v2_OK".
- **Nada se borra.** Filing reemplazado o corregido por la emisora: se archiva ambos, el
  nuevo con sufijo `_amended`. Retención mínima 7 años (Standard V(C)).
- Modelos: versionado `_YYYY-MM-DD_v#`; respaldo obligatorio antes de cada
  actualización trimestral (preflight de /update-quarter).

## brand/DESIGN.md — slots de marca (opcional)

El analista puede fijar los colores decorativos del xlsx. Formato determinista
(línea `slot: #RRGGBB`; lo parsea `tools/xlsx_builder.py::load_brand`):

```
brand_primary: #132E57    # barra de marca / cover (default navy CFI)
brand_section: #ED942D    # headers de sección (default naranja CFI)
brand_accent:  #1E8496    # acentos / tab color (default teal CFI)
```

Solo esos 3 slots son rebrandeables. Los colores SEMÁNTICOS no se tocan jamás:
azul input `FF0000FF`, verde link `FF00CC00`, rojo warn, fill amarillo de input
— son el contrato de trazabilidad, no decoración. El audit F acepta la marca
pasándole el mismo DESIGN.md.
