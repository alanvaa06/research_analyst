# Diseño — Operating/Annual split, DCF explícito, ratios unificados, cadena macro

Fecha: 2026-08-31 · Aprobado por Alan (brainstorming P1a · P2a · P3a · key=c)
Origen: hallazgos del smoke test #3 de AAPL (Cowork). Cuarta y definitiva
iteración de la forma del modelo.

## Decisiones de brainstorming

| # | Decisión | Elección |
|---|---|---|
| P1 | Granularidad de la hoja operativa | **Puro trimestral, sin columnas FY** — las columnas intercaladas del diseño anterior MUEREN; FY vive solo en la hoja anual |
| P2 | Assumptions en la hoja anual | **No** — supuestos viven UNA vez (trimestrales, Operating); la anual muestra lectura informativa de crecimientos anuales implícitos (calculada) |
| P3 | Históricos macro | **Construir `fred_fetch`** — series a `macro/series/`, tab Macro muestra observados, `/update-macro` propone el yaml |
| key | Ingreso de API key FRED | **`macro/fred.key` en el workspace** (decisión de Alan, prioriza visibilidad para su audiencia) con cascada `--api-key` → env `FRED_API_KEY` → archivo → pedirla en chat y guardarla; jamás se imprime |

## D1 — Dos hojas por granularidad y propósito

Reemplaza la hoja única `Model` y las columnas intercaladas (v0.2.6).

### `Operating` (el operating model — trimestral puro)

- Header: `1Q2016A … 4Q2031E` — solo trimestres; corte A/E en el último
  trimestre reportado; histórico trimestral = `quarterly_history_years`
  (perfil, default 10). Años anteriores al corte NO aparecen aquí (viven como
  FY observados en `Annual`).
- Secciones (outline colapsable, marcador `x` col A, labels col B):
  1. **Assumptions** — por trimestre en todo el forecast; ÚNICA zona de input
     del libro (S6). Switch de escenarios, constantes nombradas.
  2. **IS** · 3. **BS** · 4. **CF** — histórico desde `canonical_quarterly.csv`
     (capa de captura, C9), forecast por drivers.
  5. **Ratios** — `build_ratios`, UNA fila por razón cruzando histórico y
     forecast (D3).
  6. **Schedules** — bloques `Sch: <driver>` + cores (PPE, Debt, WC).

### `Annual` (agregados + valuación)

- Header: `FY2016A … FY2031E` (formatos `0"A"`/`0"E"`).
- **Cero números tecleados**: toda celda es fórmula de agregación leyendo
  `Operating`, o link a captura anual observada.
  - Flujos (IS, CF): FY = Σ de los 4 trimestres de ese año fiscal.
  - Stocks (BS): FY = valor del 4Q.
  - Ratios: RECALCULADOS sobre los agregados anuales (no promedio de ratios
    trimestrales).
  - Años pre-corte trimestral: observados anuales directos de
    `canonical_annual.csv` (misma fila, tramo distinto — F11/F12 aplican).
- Secciones: lectura informativa (crecimientos anuales implícitos de los
  supuestos trimestrales — calculada, no editable) → IS → BS → CF → Ratios →
  Schedules (agregados) → **DCF/Valuación** (D2).
- C8 estructural cruza hojas: `Annual` sin inputs; una FY tecleada = falla.

### Tabs del libro (modo `quarterly`)

`Cover · Checks · Operating · Annual · Macro · Rev_Reconcile · Val_Comps ·
Sensitivity · Summary`. La tab `Quarterly` ya no existe (la captura trimestral
vive en Operating). Modo `annual`: una sola hoja `Model` anual como hasta hoy.

## D2 — DCF línea por línea (sección de `Annual`)

Cada componente en su fila, histórico Y forecast donde aplique — cero fórmulas
comprimidas:

```
EBIT (link a Annual§IS)                          [hist + forecast]
(-) Impuestos sobre EBIT (t efectiva x EBIT)     [hist + forecast]
NOPAT                                            [hist + forecast]
(+) D&A (link)                                   [hist + forecast]
(-) Capex (link)                                 [hist + forecast]
(-) Delta working capital (link)                 [hist + forecast]
FCFF                                             [hist + forecast]
Factor de descuento                              [solo forecast]
PV de FCFF                                       [solo forecast]
Suma PV explicitos
TV Gordon = FCFF_n x (1+g) / (WACC - g)
TV exit = EBITDA_n x multiplo
PV del TV (Gordon) · PV del TV (exit)
Deuda neta actual (con desglose citado)
EV (Gordon) · EV (exit)
Equity (Gordon) · Equity (exit)
Acciones diluidas
Valor por accion — Gordon · Valor por accion — exit
Cruce: multiplo implicito del TV Gordon · g implicita del exit (check D4)
Reverse DCF: EV de mercado · TV implicita · g implicita de mercado (check D4b)
Bloque Hamada (beta pure-play, mecanica visible)
```

El FCFF histórico calculado es sanity check visible: el analista ve el FCFF
realizado junto al proyectado en la misma fila.

## D3 — Ratios: una fila, todo el horizonte

- PROHIBIDO seccionar "Ratios — histórico" y "Ratios — forecast" (bug del
  smoke #3): `build_ratios` se llama UNA vez sobre el horizonte completo.
- **Enforcement — F13 gana unicidad**: un label de `REQUIRED_RATIO_LABELS`
  apareciendo 2+ veces en la misma hoja = secciones partidas = FALLA (además
  del chequeo de completitud existente).

## D4 — Cadena macro completa

1. **`tools/fred_fetch.py`** (patrón sec_fetch/xbrl_fetch, stdlib):
   - Series default: UST 10Y (DGS10), Fed Funds (FEDFUNDS), CPI US
     (CPIAUCSL), PIB real US (GDPC1), USDMXN (DEXMXUS). Lista editable en
     `macro/fred-series.txt` (un ID por línea).
   - Salida: `macro/series/<ID>.csv` (date,value) + manifest con fuente,
     serie, fecha de descarga, `tag=observado`.
   - Key: cascada `--api-key` → env `FRED_API_KEY` → `macro/fred.key` → si
     falta y hay chat, pedirla al usuario (link de registro gratuito) y
     guardarla en `macro/fred.key`; nunca imprimirla; manejo de red bloqueada
     igual que sec_fetch (mensaje accionable).
2. **Tab `Macro` del modelo**: muestra los históricos observados de
   `macro/series/` (última observación + mini-serie anual) con fuente y fecha
   — no placeholders. `macro-view.yaml` vacío sigue siendo AVISO (D6), pero la
   tab ya no queda muerta.
3. **`/update-macro`**: propone el yaml desde `macro/series/` + `macro/sources/`,
   gate por campo (contrato existente, ahora con insumo de series).

## Cambios de contrato/código (cuando se apruebe el plan)

| Archivo | Cambio |
|---|---|
| `templates/model-spec.md` | Reescritura §tabs + §Model → Operating/Annual (D1, D2) |
| `templates/coverage-tree.md` | `macro/series/`, `macro/fred.key`, `macro/fred-series.txt` |
| `tools/xlsx_builder.py` | Header trimestral puro (reusa quarter_header); helpers de agregación FY; F13 unicidad; F14 ajustado (Operating: ≥4 A y ≥4 E; Annual: FY sin inputs); S6/F7 sobre ambas hojas |
| `tools/fred_fetch.py` | Nuevo (D4) |
| `commands/update-macro.md` | Insumo de series + pedido de key en chat |
| `skills/xlsx-building/SKILL.md` | Scaffold de dos hojas; DCF línea por línea; ratios una llamada |
| `skills/model-standards/*` | Referencias actualizadas (integrity-checks C8/S6/F7/F13/F14, excel-practices, valuation-conventions §DCF) |
| `templates/issuer-profile.yaml` | Sin cambios (quarterly + quarterly_history_years ya existen) |

## Fuera de alcance

- Banxico SIE (sigue en áreas de oportunidad).
- Modo `quarterly` para Val_Comps/Sensitivity (siguen anuales/puntuales).
- Re-run del smoke (lo corre Alan en Cowork tras el release).
