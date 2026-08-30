---
name: model-standards
description: Estándar del modelo 3 estados del plugin — construye el xlsx (estructura, convenciones Excel base CFI, checks de integridad, pestañas de valuación determinista y comps) y lo audita. Usa esta skill siempre que haya que construir un modelo financiero en Excel, correr o verificar checks de integridad (balance, tie-out de caja, reconciliación de revenue), armar pestañas de valuación (DCF, comps, DDM, NAV/AFFO, SOTP), auditar un modelo existente contra convenciones, o cuando el usuario pida "construye el modelo", "revisa mi modelo", "corre los checks", "arma la valuación" — aunque el modelo no lo haya creado este plugin.
---

# model-standards

Dueña única del xlsx. Nadie más escribe en el modelo. Construye contra dos contratos:
`templates/model-spec.md` (estructura) y `assumptions/driver-map.md` (qué schedules
existen). **Toda cifra sale de fórmula o de un input etiquetado del analista — esta
skill jamás genera un número.**

## Cuándo corre

- `/init-coverage` paso 6: construir el modelo (requiere driver-map aprobado).
- `/update-quarter` paso 4: re-correr checks tras capturar el trimestre.
- `/model-check`: solo auditoría, standalone.
- Standalone: auditar cualquier modelo contra el estándar (ver abajo).

## Inputs (contratos de entrada)

| Input | De quién | Qué trae |
|---|---|---|
| Históricos mapeados con cita | `statement-mapper` | cifras `observado` por línea |
| `assumptions/driver-map.md` | `driver-inventory` (design) | drivers clave + spec de schedules + doble ruta de revenue |
| `profile/issuer-profile.yaml` | `framework-mapper` | marco, convenciones, métodos de valuación activos |
| `macro-view.yaml` (workspace) | analista | rf, ERP, FX, decks — para tab Macro |
| `comps/*.yaml` | `statement-mapper` | snapshots para Val_Comps |

Falta un contrato → detente y repórtalo; no construyas parcial ni inventes el insumo.

## Procedimiento de construcción

1. Lee los cinco contratos. Confirma con el usuario: periodos históricos, horizonte,
   métodos activos (del perfil — puede sobreescribir).
2. Genera el xlsx con herramienta determinista (openpyxl o equivalente) siguiendo
   `model-spec.md`: tabs en orden, colores y convenciones de
   `references/excel-practices.md`.
3. **UNA sola tab `Schedules`**: un bloque `Sch: <nombre>` por driver del
   driver-map, apilados, más los bloques core (PPE, Debt, WC). Jamás una tab por
   schedule — menos tabs, mejor (check S9). El build-up de revenue sale de los
   bloques; la tab `Rev_Reconcile` cruza bottom-up vs top-down.
4. Tab `Ratios` (core, solo fórmulas) según `references/ratios-analytics.md`:
   DuPont, ROIC/economic profit, ratios estándar, CCC, DOL/DFL/DTL, screening de
   crédito (solo non_financial), calidad de utilidades.
5. Pestañas de valuación según métodos activos — fórmulas y convenciones exactas en
   `references/valuation-conventions.md` (incluye bloque Hamada, reverse DCF y
   múltiplos justificados + PVGO). Usuario en el loop en cada supuesto.
6. Corre TODOS los checks de `references/integrity-checks.md`. Cualquier rojo:
   arregla estructura/fórmulas (nunca "ajustes" a cifras observadas) y re-corre.
7. Entrega solo con checks verdes. Check rojo irresoluble = reporta FALLA con celdas
   afectadas. Un modelo que "casi cuadra" no existe.

## Modo auditoría (standalone y /model-check)

Sobre cualquier xlsx (aunque no lo haya creado el plugin): corre la lista completa de
`integrity-checks.md`, reporta `[ok]/[x]` por check con celdas afectadas. No edites
el modelo ajeno sin instrucción explícita del usuario.

Precondición standalone: ninguna. Es el punto de entrada más barato del plugin.

## Trazabilidad en el xlsx

- `observado`: input con comentario de celda citando fuente y página.
- `guidance`: input marcado como afirmación de management — nunca alimenta una
  fórmula sin que el analista lo convierta explícitamente en supuesto propio.
- `supuesto`: azul, en Assumptions, puesto por el analista.
- `output`: fórmula negra. Punto.

## Entrevista de cierre

Objetivo (preguntas adaptativas — generarlas desde lo construido y el journal, según
`templates/debate-protocol.md`): **¿el modelo captura el negocio real o solo la
contabilidad?** Sondear: qué bloque de Schedules falta, qué línea del build-up quedó
floja, si la estructura refleja cómo la emisora gana dinero. Confrontar el spread
ROIC−WACC histórico (tab Ratios) contra el moat que afirma industry-report, y la g
implícita de mercado (reverse DCF, check D4b) contra la g del analista. Registrar
en thesis-journal.

## Referencias

- `references/excel-practices.md` — convenciones CFI: leer antes de construir.
- `references/integrity-checks.md` — la lista S/C/D completa: leer antes de auditar.
- `references/valuation-conventions.md` — leer antes de armar cualquier Val_*.
- `references/ratios-analytics.md` — spec de la tab Ratios y del bloque `Sch: WC`:
  leer antes de construir Ratios o Schedules.
