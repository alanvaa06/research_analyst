# Diseño — Extensión analítica del modelo (tab Ratios + bloques de valuación)

Estado: **APLICADO a los contratos del plugin (2026-08-30)** — model-spec,
integrity-checks, valuation-conventions, ratios-analytics (nueva), driver-inventory
y model-standards actualizados. Quedan los [VERIFICAR] de §9 antes de que
model-standards construya estos bloques en un xlsx real.
Fecha: 2026-08-30
Ajuste de convención (feedback de Alan, dogfood con modelo real que generó 10 tabs
`Sch_*`): **schedules viven en UNA sola tab `Schedules`, un bloque `Sch: <nombre>`
por driver, apilados. Menos tabs, mejor.** Check S9 lo hace obligatorio. Las
menciones a `Sch_<driver>`/`Sch_WC` como tabs en este doc se leen como bloques.
Origen: gap analysis contra toolkit CFA (vault C:\Obsidian). Alcance aprobado por
Alan: puntos #1–#9 del análisis; Monte Carlo (#10) **excluido** por conflicto con
doctrina determinista (nada por generación libre; check S3 prohíbe volátiles y el
espíritu alcanza a RAND).

## Principio rector

Todo lo que agrega este diseño comparte una propiedad: **cero supuestos nuevos del
analista**, salvo dos inputs explícitos (betas de comps con fuente; estructura de
capital objetivo para relevar). Todo lo demás es fórmula sobre líneas que IS/BS/CF
ya tienen. Encaja en la doctrina sin excepciones: fórmula o input etiquetado.

---

## 1. Tab nueva: `Ratios`

Posición: después de `CF`, antes de `Sch_<driver>` (consume los 3 estados, alimenta
lectura — no cálculo — de las Val_*). Core: **siempre activa**, como IS/BS/CF.
Histórico + forecast, una fórmula por fila (check S5 aplica igual).

### Bloque A — DuPont

3 factores:

    ROE = (NI/Ventas) × (Ventas/Activos) × (Activos/Capital)
          margen neto   rotación          apalancamiento

5 factores:

    ROE = (NI/EBT) × (EBT/EBIT) × (EBIT/Ventas) × (Ventas/Activos) × (Activos/Capital)
          carga fiscal  carga int.  margen op.     rotación           apalancamiento

- Denominadores de balance: promedio de periodo ((inicio+fin)/2), consistente en
  todas las filas del tab.
- Fila de identidad: ROE directo (NI/Capital prom.) − ROE DuPont = 0. Alimenta
  check nuevo (ver §6).

### Bloque B — ROIC y economic profit

    NOPAT = EBIT × (1 − t efectiva)          ← t efectiva por fórmula desde IS
    Capital invertido = deuda total + capital contable − caja y equivalentes
    ROIC = NOPAT / Capital invertido promedio
    Economic profit = (ROIC − WACC) × Capital invertido promedio

- WACC referenciado de `Val_DCF` (link verde entre hojas — permitido; externo no).
- Lectura de tesis: spread ROIC−WACC positivo sostenido = evidencia numérica del
  moat que `industry-analysis` afirma cualitativamente. La entrevista de cierre de
  model-standards lo confronta: "el reporte de industria dice moat ancho; el spread
  histórico dice X — ¿cuadra?".

### Bloque C — Ratios estándar (actividad / liquidez / solvencia / rentabilidad)

| Grupo | Filas |
|---|---|
| Actividad | rotación inventarios, CxC, CxP, activos totales |
| Liquidez | corriente, quick, cash ratio |
| Solvencia | deuda/capital, deuda/EBITDA, deuda neta/EBITDA, cobertura de intereses (EBIT/gasto fin.), cobertura de cargos fijos |
| Rentabilidad | margen bruto, operativo, EBITDA, neto; ROA; ROE (link al Bloque A) |

### Bloque D — Ciclo de conversión de efectivo

    DIO = Inventario prom. / COGS × 365
    DSO = CxC prom. / Ventas × 365
    DPO = CxP prom. / COGS × 365
    CCC = DIO + DSO − DPO

Histórico calculado; forecast **referencia los días de `Sch_WC`** (ver §5) — el
CCC forecast es output del schedule, no fila independiente.

### Bloque E — Apalancamiento operativo/financiero

    DOL = %ΔEBIT / %ΔVentas        (por fórmula sobre periodos del modelo)
    DFL = EBIT / (EBIT − gasto financiero neto)
    DTL = DOL × DFL

Filas de lectura (no drivers). Valor principal: emisoras cíclicas apalancadas —
el debate de drivers las cita.

### Bloque F — Crédito y screening

| Métrica | Fórmula | Nota |
|---|---|---|
| Altman Z'' (mercados emergentes) | 6.56·(WC/TA) + 3.26·(RE/TA) + 6.72·(EBIT/TA) + 1.05·(BVE/TL) + 3.25 | Variante EM aplica a México; coeficientes [VERIFICAR] antes de construir |
| Piotroski F-score | 9 señales binarias estándar (rentabilidad 4, apalancamiento/liquidez 3, eficiencia 2) | Cada señal una fila auxiliar agrupada (outline); suma visible |

- Solo `issuer_type: non_financial`. Bancos/aseguradoras: bloque omitido (v2 con
  Anexo 33, igual que residual income).
- Son **screening, no veredicto**: filas de aviso, jamás gate.

### Bloque G — Calidad de utilidades

    CFO/NI                                    (por periodo)
    Accruals ratio (BS) = ΔNOA / NOA promedio
    NOA = (activos − caja) − (pasivos − deuda)

Aviso (no bloqueo) vía check D9 (§6). Corre naturalmente en `/update-quarter`.

---

## 2. `Val_DCF` — bloque beta pure-play (Hamada)

Sustituye "beta: supuesto con fuente" por mecánica visible:

    β_u de cada comp = β_l / (1 + (1−t)·(D/E))     ← una fila por comp
    β_u grupo = mediana de β_u de comps
    β_relevered = β_u grupo × (1 + (1−t)·(D/E objetivo))

Inputs del analista (los DOS únicos supuestos nuevos de todo este diseño):
- β_l de cada comp, con fuente citada (comentario de celda, etiqueta `observado`).
- D/E objetivo de la emisora (etiqueta `supuesto`, en Assumptions).

D y E de comps: de `comps/*.yaml` que ya existen (statement-mapper los puebla).
El analista puede sobreescribir el beta final (supuesto propio, documentado en
`log/decisions.md`) — la mecánica queda visible como referencia aunque no se use.

## 3. `Val_Comps` — múltiplos justificados + PVGO

Bloque nuevo debajo del grupo de comps:

    P/E justificado (leading)  = (1−b) / (r − g)
    P/E justificado (trailing) = (1−b)(1+g) / (r − g)
    P/B justificado            = (ROE − g) / (r − g)
    P/S justificado            = (E₀/S₀)(1−b)(1+g) / (r − g)
    PVGO                       = P₀ − E₁/r          (con precio de mercado actual)
    PVGO / P₀                  (% del precio que es expectativa de crecimiento)

- b, g, r, ROE: referencias a celdas que YA existen (Assumptions, Val_DCF, Ratios).
  Cero inputs nuevos.
- Lectura: múltiplo de mercado vs justificado por fila — convierte Val_Comps de
  descriptivo ("a cuánto cotizan") a normativo ("a cuánto deberían").

## 4. `Val_DCF` — bloque reverse DCF (expectativas implícitas)

Forma cerrada, sin Goal Seek, sin iteración:

    EV de mercado = mkt cap actual + deuda neta + minoritarios + preferentes
    TV implícita  = (EV − PV de FCFF explícitos) × (1 + WACC)^n
    g implícita   = WACC − FCFF_{n+1} / TV implícita

- Todo por fórmula desde filas existentes de Val_DCF + precio de mercado (que
  Val_Comps ya trae para el football field).
- Extiende el cruce D4: tercera columna junto a Gordon y exit multiple — "el
  mercado descuenta g = X; tú supones g = Y". Material de debate, no check duro.

## 5. `Sch_WC` — working capital por días (contrato con driver-inventory)

Hoy ΔWC del FCFF no tiene driver explícito → viola el espíritu del check D1.

- Schedule estándar: DIO / DSO / DPO como **inputs del analista** (azul, en
  Assumptions como todo driver), histórico calculado al lado como referencia.
- Inventario = DIO × COGS/365; CxC = DSO × Ventas/365; CxP = DPO × COGS/365;
  ΔWC del CF/FCFF sale del schedule.
- Cambio en `driver-inventory` (pasada design): el driver-map DEBE incluir fila de
  WC (días) en "Drivers de costo y capex" — o justificarla en "Líneas sin driver".
- `Sch_WC` entra al contrato de model-spec como schedule core (no depende del
  driver-map, siempre existe) — igual que Sch_PPE/Sch_Debt implícitos en checks C4/C5.

## 6. Checks nuevos (integrity-checks.md)

| # | Check | Tipo | Regla |
|---|---|---|---|
| C6 | Identidad DuPont | contable | ROE directo − ROE DuPont(5) = 0 todos los periodos |
| C7 | CCC del forecast consistente con Sch_WC | contable | Ratios (forecast) vs schedule |
| D9 | Calidad de utilidades | aviso | CFO/NI < 1 en ≥ 2 periodos consecutivos, o accruals ratio fuera de banda histórica → aviso, no bloqueo |
| D4b | g implícita de mercado vs g del analista | debate | divergencia grande → pregunta obligada en entrevista de cierre; nunca bloquea |

S1 (tabs vs contrato) cubre automáticamente `Ratios` y `Sch_WC` al entrar al
model-spec: cero checks estructurales nuevos.

## 7. Archivos a tocar cuando se apruebe construcción

| Archivo | Cambio |
|---|---|
| `templates/model-spec.md` | + fila tab `Ratios` (pos. 8), + `Sch_WC` core |
| `skills/model-standards/references/valuation-conventions.md` | + bloque Hamada en Val_DCF, + justificados/PVGO en Val_Comps, + reverse DCF, + §Ratios |
| `skills/model-standards/references/integrity-checks.md` | + C6, C7, D9, D4b |
| `skills/driver-inventory/SKILL.md` | pasada design: WC por días obligatorio en driver-map |
| `skills/model-standards/SKILL.md` | procedimiento: construir Ratios/Sch_WC; entrevista de cierre suma pregunta ROIC−WACC vs moat |
| `templates/issuer-profile.yaml` | nada — Ratios es core, sin flag de activación; bloque F condicionado por `issuer_type` ya existente |

## 8. Fuera de alcance (explícito)

- **Monte Carlo / árboles de decisión** — excluido por Alan; conflicto de doctrina.
  Escenarios discretos bull/base/bear + data tables cubren el caso de uso v1.
- Bancos/aseguradoras (bloque F, y todo lo que toque Anexo 33) — v2, junto con
  residual income.
- Ajustes de pensiones / SBC / multinacional (organic revenue, translación) — no
  descartados; no priorizados. Candidatos a v-next+1 si el dogfood los pide.

## 9. Verificaciones — CERRADAS (2026-08-30)

- Altman Z'' verificado (3 fuentes cruzadas; creditguru tenía typo 6.5→6.56;
  WallStreetPrep erraba X4 como market cap — es book value): Z'' = 6.56·WC/TA +
  3.26·RE/TA + 6.72·EBIT/TA + 1.05·BVE/TL; zonas 2.60 / 1.10 sobre Z'' sin
  constante; EM score = Z''+3.25 solo como equivalente de rating.
- Piotroski 2000 verificado: 9 señales exactas en ratios-analytics.md; ROA/CFO/
  rotación sobre TA inicial; señal 7 = sin emisión de capital común.
- NOA: minoritarios = financiamiento (dentro de capital, fuera de pasivos
  operativos), consistente con capital invertido del ROIC.

Spec completa — sin [VERIFICAR] pendientes. Lista para construcción en xlsx cuando
Alan apruebe.
