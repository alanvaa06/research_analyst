# Ratios & Analytics — spec de la tab `Ratios` y del bloque `Sch: WC`

Sección core de la hoja `Model` (siempre activa). Solo fórmulas sobre los 3
estados — **cero inputs del analista**. Histórico + forecast; una fórmula por
fila y tramo (check S5). Denominadores de balance: promedio de periodo
((inicio+fin)/2), consistente en TODAS las filas.

**Generación: SOLO vía `ModelStyler.build_ratios`** (registro canon→fila del
build; completitud y unicidad auditadas por check F13 contra
`REQUIRED_RATIO_LABELS`). Este documento es el contrato legible de lo que ese
código implementa.

**Ventanas móviles (modo trimestral)**: UDM/LTM = EXACTAMENTE 4 trimestres
(t−3 … t) — ni 5 (columna −4 a la actual: el bug del smoke #4, infla ~25%) ni
"trimestre × 4". Toda razón anualizada sobre base trimestral (DSO/DIO/DPO,
deuda/EBITDA, cobertura) usa flujos UDM y stocks promedio de los mismos 4
trimestres. La fórmula de la ventana es idéntica en toda la fila (S5).

## Bloque A — DuPont

3 factores:

    ROE = (NI/Ventas) × (Ventas/Activos) × (Activos/Capital)
          margen neto   rotación          apalancamiento

5 factores:

    ROE = (NI/EBT) × (EBT/EBIT) × (EBIT/Ventas) × (Ventas/Activos) × (Activos/Capital)
          carga fiscal  carga int.  margen op.     rotación           apalancamiento

Fila de identidad: ROE directo (NI/capital prom.) − ROE DuPont 5 = 0 → check C6.

## Bloque B — ROIC y economic profit

    NOPAT = EBIT × (1 − t efectiva)         ← t efectiva por fórmula desde IS
    Capital invertido = deuda total + capital contable − caja y equivalentes
    ROIC = NOPAT / capital invertido promedio
    Economic profit = (ROIC − WACC) × capital invertido promedio

WACC referenciado de `Val_DCF` (link verde entre hojas). Lectura de tesis: spread
ROIC−WACC positivo sostenido = evidencia numérica del moat que industry-analysis
afirma cualitativamente; la entrevista de cierre lo confronta.

## Bloque C — Ratios estándar

| Grupo | Filas |
|---|---|
| Actividad | rotación de inventarios, CxC, CxP, activos totales |
| Liquidez | corriente, quick, cash ratio |
| Solvencia | deuda/capital, deuda/EBITDA, deuda neta/EBITDA, cobertura de intereses (EBIT/gasto fin.), cobertura de cargos fijos |
| Rentabilidad | margen bruto, operativo, EBITDA, neto; ROA; ROE (link a Bloque A) |

## Bloque D — Ciclo de conversión de efectivo

    DIO = inventario prom. / COGS × 365
    DSO = CxC prom. / ventas × 365
    DPO = CxP prom. / COGS × 365
    CCC = DIO + DSO − DPO

Histórico: calculado. Forecast: referencia los días del bloque `Sch: WC` — el CCC
forecast es output del schedule, no fila independiente (check C7).

## Bloque E — Apalancamiento operativo/financiero

    DOL = %ΔEBIT / %ΔVentas       (sobre periodos del modelo)
    DFL = EBIT / (EBIT − gasto financiero neto)
    DTL = DOL × DFL

Filas de lectura, no drivers. Valor principal: emisoras cíclicas apalancadas.

## Bloque F — Crédito y screening (solo `issuer_type: non_financial`)

### Altman Z'' (verificado — Altman, Hartzell & Peck 1995)

    Z'' = 6.56·(WC/TA) + 3.26·(RE/TA) + 6.72·(EBIT/TA) + 1.05·(BVE/TL)

- BVE = capital contable a **libros** (no mercado — esa es la diferencia del Z''
  vs el Z original; aplica a privadas, no-manufactureras y EM).
- Zonas sobre Z'' sin constante: seguro > 2.60; gris 1.10–2.60; distress < 1.10.
- Fila adicional EM score = Z'' + 3.25 — estandariza para que 0 ≈ bono D;
  informativa (equivalente de rating), las zonas se leen sobre Z'' sin constante.

### Piotroski F-score (verificado — Piotroski 2000)

Nueve señales binarias (1 si cumple, 0 si no); cada una fila auxiliar agrupada
(outline), suma visible. ROA y CFO escalados por activos totales **iniciales**.

| # | Grupo | Señal = 1 si |
|---|---|---|
| 1 | Rentabilidad | ROA > 0 (NI antes de extraordinarios / TA inicial) |
| 2 | Rentabilidad | CFO > 0 (CFO / TA inicial) |
| 3 | Rentabilidad | ΔROA > 0 vs año anterior |
| 4 | Rentabilidad | CFO > ROA (accrual: caja respalda la utilidad) |
| 5 | Apalancamiento/liquidez | razón deuda LP / TA promedio bajó |
| 6 | Apalancamiento/liquidez | razón corriente subió |
| 7 | Apalancamiento/liquidez | sin emisión de capital común en el año (no dilución) |
| 8 | Eficiencia | margen bruto subió |
| 9 | Eficiencia | rotación de activos (ventas / TA inicial) subió |

Bancos/aseguradoras: bloque omitido (v2, junto con Anexo 33 y residual income).
Son **screening, no veredicto**: filas informativas, jamás gate.

## Bloque G — Calidad de utilidades

    CFO/NI                                   (por periodo)
    NOA = (activos − caja) − (pasivos − deuda)
    Accruals ratio (BS) = ΔNOA / NOA promedio

Alimenta check D9 (aviso, no bloqueo). Convención de minoritarios: son
FINANCIAMIENTO — dentro de capital, fuera de pasivos operativos de NOA
(consistente con capital invertido del Bloque B, que usa capital contable total).

---

## Bloque `Sch: WC` (en tab `Schedules` — core, siempre existe)

Working capital por días — arregla que ΔWC no tenía driver explícito (espíritu D1):

- DIO / DSO / DPO forecast = **inputs del analista** (azul, en Assumptions, como
  todo driver); histórico calculado al lado como referencia.
- Inventario = DIO × COGS/365; CxC = DSO × ventas/365; CxP = DPO × COGS/365.
- ΔWC del CF y del FCFF sale de este bloque, nunca de una fila suelta.
- driver-inventory (pasada design): el driver-map DEBE incluir la fila de WC en
  "Drivers de costo y capex" — o justificarla en "Líneas sin driver".
