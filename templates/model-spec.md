# Model Spec — estructura del xlsx estándar (v3)

Contrato que `model-standards` implementa y `/model-check` audita. Las convenciones de
formato y fórmulas viven en `skills/model-standards/references/excel-practices.md`
(base CFI); los checks en `references/integrity-checks.md`; las pestañas de valuación
en `references/valuation-conventions.md`.

Doctrina de forma (patrón CFI verificado en el corpus — su "Financial Model"
apila estados, schedules y valuación en UNA hoja con outline): **menos tabs,
mejor; el modelo vive en UNA hoja con secciones colapsables.**

## Pestañas (en este orden)

| # | Tab | Contenido | Regla |
|---|---|---|---|
| 1 | `Cover` | Propósito, versión, autor, fecha, leyenda de colores, **celda única de error check** | La celda agrega TODOS los checks del libro |
| 2 | `Checks` | Todos los checks de integridad, uno por fila, con estado | Solo fórmulas; ver integrity-checks.md |
| 3 | `Model` | **LA hoja del modelo** — secciones apiladas con outline, en este orden: **Assumptions → IS → BS → CF → DCF → Ratios → Schedules** | Ver §Model abajo. Balance check y tie-out por columna en fila 3, congelados |
| 4 | `Macro` | Valores traídos de macro/macro-view.yaml, con fuente y fecha | Solo lectura del yaml; sin inputs propios |
| — | `Quarterly` | Condicional (`annual_plus_quarterly`): captura trimestral observada + LTM + actual-vs-estimado | Alimenta calibración de /update-quarter; cross-foot C8 |
| — | `Rev_Reconcile` | Doble ruta de revenue: bottom-up (bloques Sch) vs top-down (Macro × industria × participación) | Divergencia > umbral → flag en error check |
| — | `Val_Comps` | Múltiplos POR FÓRMULA desde comps/*.yaml; media armónica; justificados + PVGO | Staleness de snapshots flaggeada |
| — | `Val_<método>` | Solo métodos activos del perfil (DDM / FCFE / NAV_AFFO / SOTP) | RI: especificado, inactivo v1 |
| — | `Sensitivity` | Data tables 2 variables, aisladas | Tab dedicada |
| — | `Summary` | Football field (métodos activos) + 3-5 outputs clave | Ejecutivo: una pantalla |

## §Model — la hoja única

Secciones con header de banda (naranja/brand) y contenido agrupado (outline
nivel 1), colapsables a vista ejecutiva:

1. **Assumptions** — TODOS los inputs del analista: drivers (del driver-map),
   bloque industry, refs a macro, switch de escenarios (una celda CHOOSE/INDEX),
   bloque de constantes nombradas (`DAYS_YEAR`, `THOUSANDS`). ÚNICA sección con
   celdas de input (azul + amarillo) — check S6 aplica por sección, no por tab.
2. **IS / BS / CF** — histórico (desde `model/inputs/canonical_*.csv`) +
   forecast, una serie = una fila (F11/F12).
3. **DCF** — FCFF multi-stage; terminal DUAL (Gordon y exit multiple cruzados);
   bloque Hamada; reverse DCF (g implícita de mercado).
4. **Ratios** — generada por `ModelStyler.build_ratios` (bloques completos:
   DuPont 3/5, ROIC + economic profit, rentabilidad/liquidez/solvencia, CCC,
   DFL, calidad de utilidades). Completitud auditada por check F13.
5. **Schedules** — un bloque `Sch: <nombre>` por driver del driver-map + cores
   (PPE, Debt, WC). Nunca una hoja por schedule (S9).

## Periodicidad (`model_periodicity` del perfil)

- `annual`: columnas anuales FY.
- `annual_plus_quarterly`: **columnas mixtas en `Model`** — trimestres ESTIMADOS
  del año fiscal en curso y el siguiente (hasta 8 columnas `#Q20yyE`) antes de
  los años anuales; los assumptions del tramo corto son TRIMESTRALES; el anual
  del año en curso = SUMA de sus trimestres (check C8 estructural, no
  verificación a posteriori). La tab `Quarterly` mantiene la captura observada
  y la calibración. Años posteriores: anuales.
- `quarterly`: forecast trimestral completo (emisoras muy estacionales).

## Reglas transversales

- Periodos en columnas, líneas en filas; flujo top-to-bottom, left-to-right.
- **Menos tabs, mejor**: el modelo completo vive en `Model`; solo lo que tiene
  granularidad o estructura distinta (Quarterly, comps, data tables, summary)
  gana tab propia.
- **Formato por código**: el libro se construye vía `tools/xlsx_builder.py`
  (skill xlsx-building); los checks F auditan paleta, fuentes, formatos,
  gridlines, freeze, outline, series y completitud de Ratios.
- **Una serie = una fila** (checks F11 y F12): histórico calculado/observado y
  forecast en la misma fila, rol por columna; nunca filas "histórico" y
  "forecast" separadas; valores derivables hacia atrás (índices, ratios
  implícitos) se POBLAN por fórmula, no se dejan vacíos.
- Una fórmula por fila POR TRAMO (S5): un tramo histórico, un tramo trimestral
  estimado (si aplica), un tramo anual estimado — idéntica dentro de cada tramo.
- Un archivo por modelo; **cero links entre libros**.
- Ninguna cifra nace de generación libre: fórmula o input etiquetado.
- Cada línea de forecast referencia un driver de la sección Assumptions —
  línea sin driver = flag de driver-inventory.
- Etiquetas de trazabilidad: observado (azul con cita en comentario), guidance
  (marcado), supuesto (azul + amarillo), output (fórmula negra), link (verde).
- Versionado `_YYYY-MM-DD_v#`; nunca borrar columnas a media serie.
