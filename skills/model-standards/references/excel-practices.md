# Excel Practices — contrato de formato (base CFI, verificado empíricamente)

Convenciones obligatorias del modelo. Fuente: corpus CFI extraído 2026-08-30
(3-Statement Model Complete, caso AMZN avanzado, Valuation Model, template
library) — valores medidos, no doctrina de blog.

**Regla cero: el formato es CÓDIGO.** Todo workbook del plugin se construye vía
`tools/xlsx_builder.py` (`ModelStyler`). Prohibido aplicar estilos con openpyxl
crudo o "a juicio": paleta, fuentes, formatos numéricos, bordes, gridlines,
freeze y outline salen del módulo. `/model-check` audita esto con los checks F
(`python tools/xlsx_builder.py audit <modelo>`), whitelists en el código.

## Estructura

- Separación por MÓDULO, nunca por schedule: los schedules viven como bloques
  `Sch: <nombre>` dentro de la única tab `Schedules` (convención CFI: el caso
  AMZN mete IS+BS+CF+schedules en una sola tab de 274 filas con outline).
- Menos tabs, mejor. El conteo de tabs del modelo es fijo (model-spec); solo
  crecen los bloques.
- Flujo top-to-bottom, left-to-right; periodos en columnas, líneas en filas.
- Un archivo por modelo; cero links entre libros.
- Cover con propósito, versión, autor, fecha, leyenda de colores y la celda
  única de error check.

## Layout de toda hoja de datos (lo aplica el builder)

- Fila 1-2: barra navy con copyright + título de hoja (16 bold blanco) +
  unidades en el header — "(USD millones salvo indicado)" — nunca en celdas.
- Fila 3: fila de CHECK por columna (ej. balance check), visible siempre.
- Fila 3/4: header de periodos con sufijo A/E (`0"A"` / `0"E"` → 2025A, 2026E).
- Freeze panes en A4/C4: título + años + check congelados al scrollear.
- Gridlines ocultas en TODAS las hojas (CFI: 100% del corpus).
- Columna A de etiquetas ancha (~42); etiquetas descriptivas, sin crípticos.
- Secciones dentro de la hoja: header con banda naranja bold 14; sub-secciones
  bold 12; contenido agrupado (outline nivel 1) para colapsar a vista resumen.

## Colores (paleta cerrada — check F3/F4)

| Uso | Valor |
|---|---|
| Barra de marca / cover | Navy `FF132E57`, texto blanco |
| Header de sección | Naranja `FFED942D` |
| Acentos / tab color dashboard | Teal `FF1E8496` |
| Input del analista | Fuente azul `FF0000FF` + fill amarillo claro `FFFFF2CC` |
| Observado (histórico citado) | Fuente azul `FF0000FF`, sin fill, comentario con fuente |
| Fórmula | Fuente negra |
| Link a otra hoja | Fuente verde `FF00CC00` |
| Error/warn | Fuente roja `FFFF0000` |
| Área de escenario | Fill gris `FFF2F2F2` |

Fuente única: **Arial Narrow** (11 normal; 11 bold subtotales; 12 bold
sub-sección; 14 bold sección; 16 bold título de hoja).

## Formatos numéricos (whitelist literal — check F5)

| Uso | Formato |
|---|---|
| Cifras (miles, negativo en paréntesis, cero como guion) | `_-* #,##0_-;\(#,##0\)_-;_-* "-"_-;_-@_-` |
| Variante negativos rojos | `#,##0_);[Red](#,##0);-` |
| Percents | `0.0%` (drivers) / `0.00%` (tasas WACC) |
| Múltiplos | `0.0\x` → "12.3x" |
| USD por acción | `"$"#,##0.00_);\("$"#,##0.00\)` |
| Años | `0"A"` / `0"E"` |
| Fechas | `mm-dd-yy` |
| Celda auxiliar invisible | `;;;` |

## Fórmulas

- Una fórmula por fila, copiada idéntica en todos los periodos (check S5).
- Jamás números hard-coded en fórmulas (check S4). Constantes de conversión
  (365, 1000) viven como celdas etiquetadas en Assumptions con named range
  (`DAYS_YEAR`, `MM_TO_B`) creado por `ModelStyler.define_constant`.
- Named ranges SOLO para valores clave cross-tab (precio de mercado, acciones,
  WACC) y constantes — nunca en el cálculo fila a fila (convención AMZN).
- Fila de años por fórmula (`=+J2+1`); trimestres con `EOMONTH`/`DATE`.
- Schedules como roll-forward: Opening / Plus / Less / Closing; **interés sobre
  saldo de apertura** (mata la circularidad sin switch de iteración).
- IFERROR solo para errores esperados (múltiplo "na" en comps/precedents) y en
  la celda de check — nunca para tapar errores reales.
- Sin volátiles (OFFSET, INDIRECT, NOW, TODAY — check S3). INDEX/MATCH sobre
  VLOOKUP. Anclas `$` deliberadas (data tables).

## Integridad y controles

- Check por columna en fila 3 de IS/BS/CF (estilo AMZN:
  `=+IF(ABS(ref1-ref2)>0.0001,"Error","OK")`).
- Tab `Checks` con la lista S/C/D en fórmulas; celda única de error en Cover
  agregando todo.
- Cálculo automático, nunca manual (el builder lo fija).
- Sin referencias circulares.

## Bordes y legibilidad

- `top: thin` sobre subtotales; `bottom: double` en totales finales.
- Subtotales bold; totales bold.
- Filas de soporte agrupadas (outline) — la hoja colapsa a vista ejecutiva.
- Escenarios: una celda switch (INDEX/CHOOSE) en Assumptions; casos bull/base/
  bear documentados; áreas de escenario con fill gris.

## Workflow

- Versionado `_YYYY-MM-DD_v#`; nunca borrar columnas a media serie.
- Todo supuesto no obvio con comentario de celda.
- Summary de una pantalla con football field y 3-5 outputs clave.
- Antes de entregar: `python tools/xlsx_builder.py audit <modelo>` en verde +
  checks S/C/D verdes. Un check rojo = FALLA, no "casi cuadra".
