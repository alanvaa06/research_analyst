---
name: xlsx-building
description: Construcción determinista del xlsx del plugin — TODO workbook se arma vía tools/xlsx_builder.py (ModelStyler), jamás con openpyxl crudo; formato (paleta brandeable desde brand/DESIGN.md, fuentes, formatos numéricos, gridlines, freeze, outline, bordes, series continuas hist→forecast) sale del código y se verifica con los checks F1-F11; incluye el modo REBUILD para reconstruir cualquier modelo existente al estándar con audit previo y paridad de números obligatoria. Usa esta skill siempre que haya que crear o editar un archivo Excel del plugin, aplicar o corregir formato de un modelo, reconstruir un modelo viejo o ajeno, correr el audit de formato, aplicar colores de marca, o cuando el usuario diga "construye el xlsx", "formatea el modelo", "el modelo salió feo", "reconstrúyelo al estándar", "corre el audit de formato" — model-standards la invoca en su paso de construcción y es obligatoria: si un xlsx se va a escribir y esta skill no está en uso, detente y cárgala.
---

# xlsx-building

Capa determinista de construcción. Regla única: **ningún workbook del plugin se
escribe sin `tools/xlsx_builder.py`**. El módulo es la implementación; esta
skill es el procedimiento; los checks F son la verificación. Prosa no construye
formato — código sí (lección del smoke test AAPL 2026-08-30: el agente tenía
las best practices escritas y entregó Calibri con gridlines).

## Procedimiento

0. **Marca**: si existe `brand/DESIGN.md` en la cobertura, cárgalo con
   `load_brand(path)` y pásalo a `ModelStyler(brand=...)` — rebrandea SOLO los
   3 slots decorativos (primary/section/accent). Los colores semánticos (azul
   input, verde link, rojo warn, fills) jamás cambian. El audit se corre con el
   mismo archivo: `python tools/xlsx_builder.py audit <modelo> brand/DESIGN.md`.
1. **Scaffold**: instancia `ModelStyler` (fija calc auto + sello F10). Crea cada
   tab con `new_sheet` (gridlines off + freeze), `brand_bar`, `label_col_width`,
   `period_header` (sufijos A/E). Tabs y orden: `templates/model-spec.md`.
2. **Secciones**: `section_header` (banda naranja) / `subsection`. En la tab
   `Schedules`: un bloque por schedule con `schedule_block_header` ("Sch: X") y
   `group_rows` sobre el contenido — JAMÁS una hoja por schedule.
3. **Contenido**: toda celda vía `set_cell` con su `CellRole` (INPUT / OBSERVED /
   FORMULA / LINK / WARN / LABEL) y `NumFmt` de la whitelist. El role fija color
   y fill — no elijas colores. Series (drivers, líneas de estados): vía
   `series_row` — histórico calculado y forecast en LA MISMA fila (check F11),
   jamás filas hist/forecast separadas ni columnas históricas vacías.
4. **Constantes**: 365, 1000 y similares como celdas etiquetadas en Assumptions
   con `define_constant` (`DAYS_YEAR`, `MM_TO_B`); las fórmulas referencian el
   named range, nunca el literal (check S4).
5. **Checks arriba**: `check_row` en fila 3 de IS/BS/CF (balance / tie-out por
   columna, estilo `=+IF(ABS(a-b)>0.0001,"Error","OK")`).
6. **Bordes**: `subtotal_border` / `total_border` — no bordes manuales.

**Ejemplo mínimo del API** (ancla la forma correcta de usarlo):

```python
styler = ModelStyler(brand=load_brand("brand/DESIGN.md"))  # brand opcional
ws = styler.new_sheet("IS", freeze="C4")
styler.brand_bar(ws, "Estado de resultados")
styler.period_header(ws, 3, 3, PeriodHeader(2019, 2031, 2025))  # 2025A|2026E
styler.series_row(ws, 7, "Crecimiento de ventas (%)", first_col=3,
                  hist_values=["=D6/C6-1", ...],   # calculado, negro
                  forecast_values=[0.05, ...],      # input, azul+amarillo
                  numfmt=NumFmt.PCT1)
styler.total_border(ws, 26, 3, 13)
styler.save(path)  # luego: python tools/xlsx_builder.py audit <path>
```
7. **Verificación obligatoria antes de entregar**:

   ```
   python tools/xlsx_builder.py audit <modelo.xlsx>
   ```

   Exit 0 = formato verde. Exit 1 = FALLA: corrige y re-corre. Nunca entregues
   con audit rojo. Luego corren S/C/D (integrity-checks.md).

## Modo rebuild (modelo existente → modelo al estándar)

Cuando el usuario entrega un xlsx (del plugin viejo o ajeno) y pide
reconstruirlo, el orden es fijo:

1. **Audit primero**: corre la lista completa S/C/D/F sobre el modelo viejo
   (`integrity-checks.md` + `python tools/xlsx_builder.py audit`). Presenta la
   tabla de violaciones — QUÉ viola y POR QUÉ se va a reconstruir.
2. **Gate**: mostrar al usuario qué se PRESERVA (valores, etiquetas de fila,
   lógica de fórmulas, supuestos) y qué se DESCARTA (todo el formato, tabs
   `Sch_*`, series partidas). Sin aprobación no hay rebuild.
3. **Rebuild**: el modelo viejo es FUENTE DE CONTENIDO, jamás de formato —
   extrae valores/labels/fórmulas con openpyxl y reconstruye vía `ModelStyler`
   contra el model-spec vigente. Versión nueva `_YYYY-MM-DD_v#`; el original
   queda intacto (nada se borra).
4. **Re-audit + paridad (obligatorio)**: checks F en verde Y check de paridad —
   los outputs clave del viejo y el nuevo coinciden (balance check, revenue por
   periodo, resultado de valuación). Divergencia = FALLA con celdas afectadas:
   reconstruir jamás cambia números en silencio. Diferencias INTENCIONALES
   (ej. corregir un hardcode) se listan explícitas en el reporte.

## Qué NO hace esta skill

- No decide contenido ni supuestos (eso es driver-inventory / el analista).
- No inventa estilos: si necesitas un formato que no está en la whitelist, la
  respuesta es proponer extender `xlsx_builder.py` + checks F con el usuario —
  no aplicarlo ad hoc.
- No toca modelos externos sin instrucción (audit sí — es solo lectura).

## Referencias

- `tools/xlsx_builder.py` — implementación única (paleta, NumFmt, roles, audit F).
- `skills/model-standards/references/excel-practices.md` — el contrato legible.
- `skills/model-standards/references/integrity-checks.md` — checks F en la lista.
