# Model Spec — estructura del xlsx estándar

Contrato que `model-standards` implementa y `/model-check` audita. Las convenciones de
formato y fórmulas viven en `skills/model-standards/references/excel-practices.md`
(base CFI); los checks en `references/integrity-checks.md`; las pestañas de valuación
en `references/valuation-conventions.md`.

## Pestañas (en este orden)

| # | Tab | Contenido | Regla |
|---|---|---|---|
| 1 | `Cover` | Propósito, versión, autor, fecha, leyenda de colores, **celda única de error check** | La celda agrega TODOS los checks del libro |
| 2 | `Checks` | Todos los checks de integridad, uno por fila, con estado | Solo fórmulas; ver integrity-checks.md |
| 3 | `Assumptions` | TODOS los inputs del analista en un solo bloque: drivers (de driver-map), bloque industry, refs a macro-view, switch de escenarios | Única tab con celdas de input (azul/amarillo); una celda switch CHOOSE/INDEX; bull/base/bear documentados |
| 4 | `Macro` | Valores traídos de macro-view.yaml, con fuente y fecha | Solo lectura del yaml; sin inputs propios |
| 5 | `IS` | Estado de resultados histórico + forecast | Una fórmula por fila, copiada idéntica |
| 6 | `BS` | Balance | Balance check en el header de la hoja |
| 7 | `CF` | Flujo de efectivo | Tie-out: caja final CF = caja BS |
| 8 | `Ratios` | DuPont 3/5, ROIC + economic profit, ratios estándar, CCC, DOL/DFL/DTL, crédito/screening, calidad de utilidades | Solo fórmulas sobre IS/BS/CF; ver ratios-analytics.md |
| 9 | `Schedules` | **UNA sola tab**: un bloque por schedule, apilados top-to-bottom. Bloques core siempre presentes: `Sch: PPE`, `Sch: Debt`, `Sch: WC`. Un bloque más por driver del driver-map (ej. `Sch: Stores`, `Sch: Copper`) | Header de bloque en col. A con prefijo `Sch: `; el driver-map es el contrato: cada bloque que pide, existe. Nunca una tab por schedule |
| — | `Rev_Reconcile` | Doble ruta de revenue: bottom-up (bloques de Schedules) vs top-down (Macro × industria × participación) | Divergencia > umbral → flag en error check |
| — | `Val_DCF` | FCFF multi-stage; terminal DUAL: Gordon Y exit multiple, cruzados | Gordon implica múltiplo; exit implica g; ambos visibles |
| — | `Val_Comps` | Múltiplos calculados POR FÓRMULA desde comps/*.yaml; media armónica | Staleness de snapshots flaggeada |
| — | `Val_<método>` | Solo métodos activos en issuer-profile (DDM / FCFE / NAV_AFFO / SOTP) | RI: especificado, inactivo v1 |
| — | `Sensitivity` | Data tables 2 variables, aisladas | Tab dedicada — no ensucia el modelo |
| — | `Summary` | Football field (solo métodos activos) + 3-5 outputs clave | Ejecutivo: una pantalla |

## Reglas transversales

- Periodos en columnas, líneas en filas; flujo top-to-bottom, left-to-right.
- **Menos tabs, mejor**: schedules SIEMPRE como bloques dentro de `Schedules`, jamás
  tabs sueltas. El conteo de tabs del modelo es fijo; solo crecen los bloques.
- **Formato por código**: el libro se construye vía `tools/xlsx_builder.py`
  (skill xlsx-building); los checks F auditan paleta, fuentes, formatos,
  gridlines, freeze y outline.
- Bloques de `Schedules`: header `Sch: <nombre>` en col. A, filas del bloque
  agrupadas (outline) para colapsar; una fila en blanco entre bloques.
- Un archivo por modelo; **cero links entre libros**.
- Ninguna cifra nace de generación libre: fórmula o input etiquetado.
- Cada línea de forecast referencia un driver de `Assumptions` — línea sin driver =
  flag de driver-inventory.
- Etiquetas de trazabilidad: input observado (con cita en comentario de celda),
  guidance (marcado), supuesto (azul), output (fórmula negra).
- Versionado `_YYYY-MM-DD_v#`; nunca borrar columnas a media serie — insertar al final.
