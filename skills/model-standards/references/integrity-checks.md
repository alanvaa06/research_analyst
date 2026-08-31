# Integrity Checks — la lista que corre /model-check

Cada check es determinista: fórmula en la tab `Checks` o escaneo por código (openpyxl).
La celda de error del Cover agrega TODOS. Un check rojo = el comando reporta FALLA,
nunca éxito. Orden: estructura → contabilidad → contenido → formato.

Los checks F corren con `python tools/xlsx_builder.py audit <modelo.xlsx>` —
implementación única, cero interpretación del agente.

## Estructurales (escaneo por código)

| # | Check | Cómo |
|---|---|---|
| S1 | Todas las tabs del model-spec v3 presentes (Cover, Checks, **Model**, Macro, condicionales); en la sección Schedules de `Model`, un bloque `Sch: <nombre>` por schedule del driver-map + cores (PPE, Debt, WC) | openpyxl: nombres de hoja vs contrato; escaneo de col. A por headers `Sch: ` vs driver-map |
| S9 | Schedules como bloques, no como tabs: ninguna hoja con nombre `Sch_*` o `Sch *`; tampoco hojas `IS`/`BS`/`CF`/`Val_DCF` sueltas (viven como secciones de `Model`) | escaneo de nombres de hoja |
| S2 | Cero links externos a otros libros | escaneo de fórmulas por `[` |
| S3 | Sin funciones volátiles (OFFSET, INDIRECT, NOW, TODAY) | escaneo de fórmulas |
| S4 | Sin números hard-coded dentro de fórmulas (fuera de Assumptions) | escaneo: constantes en fórmulas de tabs de cálculo |
| S5 | Una fórmula por fila: fórmula idéntica (relativa) en todos los periodos | comparación de R1C1 por fila |
| S6 | Inputs solo en la SECCIÓN Assumptions de `Operating` (o `Model` en modo annual); resto del libro — `Annual` incluida — sin celdas de input | escaneo: fill de input fuera del rango de la sección = falla |
| S7 | Modo de cálculo automático, no manual | propiedad del libro |
| S8 | Versionado del archivo cumple `_YYYY-MM-DD_v#` | nombre de archivo |

## Contables (fórmulas en tab Checks)

| # | Check | Fórmula |
|---|---|---|
| C1 | Balance cuadra cada periodo | A − (P + C) = 0, todos los periodos |
| C2 | Tie-out de caja | caja final CF = caja BS, todos los periodos |
| C3 | Roll de utilidades retenidas | RE₁ = RE₀ + NI − dividendos |
| C4 | Depreciación acumulada consistente con schedule | BS vs bloque `Sch: PPE` de Schedules |
| C5 | Interés consistente con schedule de deuda | IS vs bloque `Sch: Debt` (documentar switch si hay circularidad) |
| C6 | Identidad DuPont | ROE directo (NI/capital prom.) − ROE DuPont 5 factores = 0, todos los periodos (tab Ratios) |
| C7 | CCC del forecast consistente con schedule de WC | Ratios (forecast) vs días DIO/DSO/DPO del bloque `Sch: WC` |
| C8 | Agregado anual estructural (modo `quarterly`) | La hoja `Annual` es 100% fórmulas: cada FY del tramo trimestral agrega los 4 trimestres de `Operating` (flujos = Σ4Q; stocks = 4Q; ratios recalculados); pre-corte, links a canonical_annual. Un número tecleado en `Annual` = falla (F14 lo detecta por fill de input) |
| C9 | Histórico del xlsx = capa de captura | Escaneo por código: celdas históricas de IS/BS/CF coinciden con `model/inputs/canonical_annual.csv` (y `canonical_quarterly.csv` si aplica), tolerancia de redondeo; discrepancia = falla de captura o edición manual del histórico |

## De contenido (doctrina del plugin)

| # | Check | Regla |
|---|---|---|
| D1 | **Cobertura de drivers**: cada línea de forecast referencia un input de Assumptions | línea sin driver = flag (driver-inventory la reporta) |
| D2 | **Reconciliación de revenue**: ruta bottom-up (schedules) vs top-down (PIB × industria × participación) | divergencia > umbral (default 10%) = flag: supuesto roto |
| D3 | **Staleness de comps**: `as_of` de cada snapshot dentro de `stale_days` | snapshot viejo = flag en Val_Comps |
| D4 | **Cruce de terminales**: múltiplo implícito por Gordon y g implícita por exit multiple, ambos visibles | divergencia grande = revisar g o múltiplo con el analista |
| D5 | **Convergencia de métodos**: si DDM/FCFE/RI activos junto a DCF, divergencia extrema entre métodos se reporta como supuesto inconsistente | nunca se "promedia" para ocultarla |
| D6 | **Staleness de macro-view**: `updated_at` dentro de `staleness_warn_months` | aviso, no bloqueo |
| D7 | **Monitor NIF B-10**: si emisora NIF y acumulado trienal en macro-view ≥ 22%, exigir escenario de reconexión pre-modelado | ver framework-mapper reference |
| D8 | Etiquetas de trazabilidad presentes: inputs con comentario de fuente (observado) o marca guidance/supuesto | muestreo por tab |
| D9 | **Calidad de utilidades**: CFO/NI < 1 en ≥ 2 periodos consecutivos, o accruals ratio fuera de la banda histórica de la emisora | aviso, no bloqueo; material de entrevista |
| D10 | **Staleness de industry-report**: fecha del reporte más reciente en `research/industry/` dentro de `industry_staleness_months` (issuer-profile, default 6) | aviso, no bloqueo — recomendar `/update-industry` |
| D4b | **g implícita de mercado** (reverse DCF en Val_DCF) vs g terminal del analista | divergencia grande = pregunta obligada en entrevista de cierre; nunca bloquea |

## De formato (checks F — `tools/xlsx_builder.py audit`)

Whitelists exactas viven en el código (`tools/xlsx_builder.py`), derivadas del
corpus CFI (2026-08-30). El builder pasa estos checks por construcción; un modelo
externo se audita igual.

| # | Check | Regla |
|---|---|---|
| F1 | Gridlines ocultas | `showGridLines = False` en TODAS las hojas visibles |
| F2 | Fuente estándar | Una sola familia (Arial Narrow) en celdas usadas |
| F3 | Colores de fuente | Whitelist: negro, azul input `FF0000FF`, verde link `FF00CC00`, rojo warn, blanco |
| F4 | Paleta de fills | Whitelist: navy `FF132E57`, naranja `FFED942D`, teal `FF1E8496`, amarillo input `FFFFF2CC`, gris escenario. Con `brand/DESIGN.md` presente, sus 3 slots se suman a la whitelist (pasar el archivo al audit) |
| F5 | Formatos numéricos | Whitelist literal (miles con paréntesis y guion-cero, %, 0.0x, USD, fecha, A/E, `;;;`) |
| F6 | Freeze panes | Presente en hojas de datos (Assumptions/IS/BS/CF/Ratios/Schedules/Rev_Reconcile/Val_*) |
| F7 | Outline POR SECCIÓN | En `Operating` y `Annual` (o `Model`/`Schedules` legacy): CADA sección con contenido (marcador `x` + header bold) tiene filas agrupadas — agrupar solo algunas secciones FALLA |
| F8 | Sin hojas basura | Ninguna `Sch_*`, `Hoja1`, `Sheet1` (refuerza S9) |
| F9 | Headers de periodo A/E | Formatos `0"A"` / `0"E"` presentes en la fila de años |
| F10 | Sello del builder | Custom property `research_analyst_builder` presente — el modelo se construyó vía `tools/xlsx_builder.py`. En modelo externo: `[aviso]`, no falla |
| F11 | **Continuidad de series** | Una serie = UNA fila continua en todo el horizonte: histórico calculado/observado y forecast en la misma fila (el rol cambia por columna), jamás columnas históricas vacías. Detección: toda fila con ≥3 celdas de input (fill amarillo) en columnas de periodo debe tener TODAS las columnas de periodo pobladas. Requiere headers A/E (F9) para ubicar las columnas — F9 rojo deja F11 sin efecto |
| F12 | **Sin series partidas** | Fila cuyo label contiene "forecast" con la mitad histórica (columnas A) vacía, o "histórico" con la mitad estimada (columnas E) vacía = la serie se partió en dos filas. Complementa F11 (que solo vigila filas de input); cacha el patrón exacto del smoke AAPL. Derivables hacia atrás (índices, ratios implícitos) se POBLAN por fórmula |
| F13 | **Ratios completa y ÚNICA** | (i) Completitud: el set completo de `REQUIRED_RATIO_LABELS` (~25) presente; (ii) UNICIDAD: cada razón UNA sola vez por hoja — un label duplicado delata secciones "Ratios histórico"/"Ratios forecast" partidas (bug del smoke #3); la serie completa vive en una fila. `build_ratios` cumple por construcción |
| F14 | **Modelo trimestral-nativo** | Con sello `periodicity=quarterly`: (i) `Operating` trae ≥4 trimestres `A` y ≥4 `E` en el header — el modelo se CONSTRUYE sobre trimestres; (ii) `Annual` es FY-solo (cero columnas `#Q`) y sin UNA sola celda de input. Sin sello: n/a |

## Reporte de /model-check

```
[ok] / [x] por check, agrupado S / C / D / F
Resumen: N ok, M fallas, K avisos
Falla => exit report "FALLA", lista de celdas/hojas afectadas, siguiente acción sugerida
```
