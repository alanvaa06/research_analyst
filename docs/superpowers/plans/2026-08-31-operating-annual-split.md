# Operating/Annual Split Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implementar el spec 2026-08-31 — modelo en dos hojas (Operating trimestral puro / Annual agregados + DCF línea por línea), ratios en una sola fila con enforcement de unicidad, y cadena macro completa vía fred_fetch.

**Architecture:** Todo el enforcement vive en `tools/xlsx_builder.py` (checks F) y los contratos en `templates/` + `skills/`; `fred_fetch.py` replica el patrón de sec_fetch/xbrl_fetch. Verificación = demo del builder en verde + pruebas de mensaje del tool sin key/sin red.

**Tech Stack:** Python stdlib + openpyxl (existente); Markdown de contratos; FRED API (fred.stlouisfed.org/graph/fredgraph.csv — sin key para CSV público, con key para API JSON; usamos el endpoint API `api.stlouisfed.org/fred/series/observations` con key).

Spec: `docs/superpowers/specs/2026-08-31-operating-annual-split-design.md`

---

### Task 1: xlsx_builder — F13 unicidad + hojas Operating/Annual reconocidas

**Files:**
- Modify: `tools/xlsx_builder.py` (FROZEN_SHEET_PREFIXES, F7 host, F13, F14)

- [ ] **Step 1:** FROZEN_SHEET_PREFIXES: agregar "Operating", "Annual" al inicio.
- [ ] **Step 2:** F7: host = primera hoja en ("Operating", "Annual", "Model", "Schedules"); auditar por sección en TODAS las hojas de esa lista presentes (loop, acumular ungrouped con prefijo de hoja).
- [ ] **Step 3:** F13: escanear hojas ("Operating", "Annual", "Model", "Ratios"); además de completitud, contar apariciones POR HOJA de cada required label: label con ≥2 apariciones en la misma hoja ⇒ falla "secciones de Ratios partidas" (detalle con hoja y label). Implementación: `counts: dict[tuple[sheet,label], int]`.
- [ ] **Step 4:** F14 rework: con sello quarterly — (i) hoja `Operating` (o Model legacy) con ≥4 trimestres A y ≥4 E en header; (ii) si existe hoja `Annual`: su header solo años numéricos A/E (cero labels `#Q`) Y ninguna celda con INPUT_FILL en Annual (los agregados no se teclean). Detalle reporta ambas partes.
- [ ] **Step 5:** Demo: sin cambios de contenido; correr `python tools/xlsx_builder.py demo <scratch>` ⇒ `Resumen F: 14 ok, 0 fallas` (F13 unicidad no dispara: labels una vez).
- [ ] **Step 6:** Commit `feat: F13 unicidad de ratios + F7/F14 sobre Operating/Annual`.

### Task 2: tools/fred_fetch.py (nuevo)

**Files:**
- Create: `tools/fred_fetch.py`

- [ ] **Step 1:** Escribir el tool (patrón xbrl_fetch): constantes `DEFAULT_SERIES = {"DGS10": "UST 10Y", "FEDFUNDS": "Fed Funds", "CPIAUCSL": "CPI US", "GDPC1": "PIB real US", "DEXMXUS": "USDMXN"}`; lectura opcional de `macro/fred-series.txt` (un ID por línea, `#` comenta); resolución de key en cascada `--api-key` → env `FRED_API_KEY` → `<dest>/../fred.key` (o `--key-file`) → SystemExit con mensaje que instruye pegar la key en el chat para que el agente la guarde en `macro/fred.key` + link de registro; la key JAMÁS se imprime (en errores, redactarla de URLs). Endpoint: `https://api.stlouisfed.org/fred/series/observations?series_id=<ID>&api_key=<KEY>&file_type=json`. Salida: `macro/series/<ID>.csv` (`date,value`) + `macro/series/manifest.csv` (series, título, fuente="FRED", fetched_at=fecha de la última observación — NO reloj local, unidades). Red bloqueada ⇒ mensaje accionable (patrón BLOCKED_MSG con dominio api.stlouisfed.org). CLI: `python tools/fred_fetch.py [--dest macro/series] [--api-key ...] [--series A,B]`. Consola ASCII.
- [ ] **Step 2:** Probar sin key: `python tools/fred_fetch.py --dest <scratch>` ⇒ exit con mensaje de cascada/registro, sin traceback, sin key impresa.
- [ ] **Step 3:** Sintaxis: `python -c "import ast; ast.parse(open('tools/fred_fetch.py',encoding='utf-8').read())"`.
- [ ] **Step 4:** Commit `feat: fred_fetch — series macro FRED a macro/series/ con cascada de key`.

### Task 3: Contratos — model-spec (Operating/Annual + DCF explícito)

**Files:**
- Modify: `templates/model-spec.md`

- [ ] **Step 1:** Reescribir §Pestañas y §Model conforme al spec D1: tabs modo quarterly = `Cover · Checks · Operating · Annual · Macro · Rev_Reconcile · Val_Comps · Sensitivity · Summary`; sección `Operating` (trimestral puro, secciones 1-6, única zona de input) y `Annual` (cero tecleo, agregación Σ4Q/4Q/recalculado, años pre-corte desde canonical_annual, lectura informativa de crecimientos, DCF). Incluir la lista D2 de filas del DCF VERBATIM del spec (bloque de código). Ratios: una sola llamada, una fila por razón (D3). Nota: columnas intercaladas y tab Quarterly ELIMINADAS (diseño 2026-08-31 reemplaza al 2026-08-30).
- [ ] **Step 2:** Commit `docs: model-spec v4 — Operating/Annual split y DCF linea por linea`.

### Task 4: Contratos — coverage-tree + update-macro + skills

**Files:**
- Modify: `templates/coverage-tree.md` (macro/: series/, fred.key, fred-series.txt)
- Modify: `commands/update-macro.md` (insumo series; flujo de key en chat)
- Modify: `skills/xlsx-building/SKILL.md` (scaffold dos hojas; DCF filas; ratios una vez; F13 unicidad)
- Modify: `skills/model-standards/SKILL.md` (procedimiento: Operating/Annual)
- Modify: `skills/model-standards/references/integrity-checks.md` (C8 cruza hojas; F7/F13/F14 textos; S6 = sección Assumptions de Operating)
- Modify: `skills/model-standards/references/excel-practices.md` (estructura dos hojas)
- Modify: `skills/model-standards/references/valuation-conventions.md` (Val_DCF → sección DCF de Annual, filas D2)
- Modify: `README.md` (flujo paso 6: dos hojas; extras macro: series FRED)

- [ ] **Step 1:** Aplicar las 8 ediciones (texto conforme al spec D1-D4).
- [ ] **Step 2:** Grep de residuos: `grep -rn "intercalad\|tab Quarterly\|interleaved" templates skills commands README.md` ⇒ solo menciones históricas/deprecación deliberadas.
- [ ] **Step 3:** Commit `docs: contratos v4 — dos hojas, macro con series, DCF explicito`.

### Task 5: Verificación integral + release

- [ ] **Step 1:** Demo builder ⇒ 14/14.
- [ ] **Step 2:** `python tools/fred_fetch.py --dest <scratch> --api-key TESTKEY --series DGS10` contra red real ⇒ 400 de FRED (key inválida) manejado con mensaje claro SIN imprimir la key (valida ruta de red + manejo de error API).
- [ ] **Step 3:** Bump `.claude-plugin/plugin.json` a `0.3.0` (cambio estructural), commit, push, tag `v0.3.0`.
- [ ] **Step 4:** Actualizar memoria del proyecto.

## Self-review

- Cobertura del spec: D1→Tasks 1,3,4 · D2→Tasks 3,4(valuation-conventions) · D3→Tasks 1,3,4 · D4→Tasks 2,4 · cascada key→Task 2 · checks→Task 1. Sin huecos.
- Sin placeholders; nombres consistentes (Operating/Annual, F13/F14, macro/series/).
- Alcance: un solo plan, ejecutable en esta sesión.
