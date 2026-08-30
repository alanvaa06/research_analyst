---
name: driver-inventory
description: Drivers y revenue build-up del modelo — diseña los drivers clave del negocio (precio de commodity, unidades, m², volumen/precio/mix) ANTES de construir el modelo, especifica los schedules que el xlsx debe tener, reconcilia la ruta bottom-up contra la top-down, y después puebla e itera el forecast con los valores del analista, contrasta contra guidance y lleva el registro de calibración. Usa esta skill siempre que haya que identificar los drivers de una emisora, armar el revenue build-up, revisar qué líneas del forecast no tienen driver explícito, contrastar forecast vs guidance, medir precisión actual-vs-estimado, o cuando el usuario diga "¿cuáles son los drivers?", "arma el build-up", "puebla el forecast", "¿qué tan bien estimé el trimestre?".
---

# driver-inventory

Dueña única de `assumptions/driver-map.md`, del contenido de assumptions y de
`log/forecast-accuracy.md`. Corre en DOS pasadas: **design** (antes del modelo —
decide QUÉ schedules existen) y **populate** (después — les pone valores). El
principio: un forecast de "crecimiento de ingresos %" no es un forecast; precio ×
volumen sí.

## Pasada 1 — DESIGN (`/init-coverage` paso 5)

Inputs: `industry-report.md` (economía de la industria) + históricos mapeados
(unit economics visibles, KPIs revelados, segmentos) + `macro-view.yaml`.

1. Deriva candidatos a driver DESDE la industria: price-taker de commodity ⇒ deck de
   precio × volumen; industria de rollout ⇒ unidades × productividad por unidad;
   servicios ⇒ clientes × ARPU; etc. Los históricos validan (¿qué KPIs revela la
   emisora? ¿qué explica la varianza histórica de revenue?).
2. Construye el **revenue build-up en doble ruta**:
   - bottom-up: Σ segmentos (driver físico × precio) — esto define los bloques
     `Sch: <driver>` de la tab `Schedules` (UNA sola tab, un bloque por schedule;
     nunca una tab por driver);
   - top-down: PIB (macro-view) × crecimiento de industria vs PIB (industry-report)
     × participación de la emisora.
   Ambas van al modelo y se reconcilian por fórmula (`Rev_Reconcile`, check D2).
3. Drivers de costo y capex también: el cobre es revenue para la minera y costo para
   el cablero. Cada línea material del modelo → su driver. **Working capital por
   días (DIO/DSO/DPO) es obligatorio** en esta sección — alimenta el bloque core
   `Sch: WC` — o se justifica explícitamente en "Líneas sin driver".
4. Cada driver ancla EXPLÍCITAMENTE a: supuesto de industria (sección 7 del reporte),
   deck de macro-view, guidance (etiquetado), o supuesto propio de la emisora.
5. Escribe `driver-map.md` (formato abajo). Gate: el usuario aprueba el mapa — este
   es el contrato de entrada de model-standards.

### Formato de driver-map.md

```markdown
# Driver Map — <TICKER>   [fecha]
## Revenue build-up (bottom-up)
| Segmento | Driver físico | Driver de precio | Bloque (`Sch: <nombre>`) | Ancla |
## Ruta top-down
PIB (macro-view) × industria vs PIB (industry-report §2) × participación (§3) — umbral de reconciliación: X%
## Drivers de costo y capex
| Línea | Driver | Bloque (`Sch: <nombre>`) | Ancla |
## Líneas sin driver (deuda técnica del forecast)
| Línea | Por qué no tiene | Plan |
```

## Pasada 2 — POPULATE (`/init-coverage` paso 7)

1. Recorre el driver-map contra el modelo construido: **el analista pone cada
   número** — la skill estructura la sesión, driver por driver, y NUNCA propone el
   valor (puede mostrar el histórico observado y el guidance etiquetado como
   referencia; decidir es del analista). El histórico calculado de cada driver
   (crecimiento %, margen, días) vive en LA MISMA fila que el forecast (check
   F11) — al poblar, el analista ve su serie realizada al lado de lo que teclea.
2. Flag de líneas sin driver que sigan forecasteadas "por inercia".
3. Contraste vs guidance: donde el supuesto del analista difiere del guidance,
   registrar la diferencia y el porqué en `log/decisions.md` (es información de
   tesis, no un error).

## Mantenimiento (`/update-quarter` paso 5) — calibración

1. Actual (recién capturado por statement-mapper) vs driver estimado, por driver.
2. Append a `log/forecast-accuracy.md`: driver, estimado, actual, error %, fecha.
   Con historia suficiente, calcula sesgo por driver (¿siempre optimista en
   volumen?).
3. Ese sesgo documentado alimenta la entrevista adaptativa: el debate cita TU
   registro, no impresiones.

## Entrevista de cierre

- **Design — el debate central del pipeline** (per `templates/debate-protocol.md`):
  ¿cuáles son LOS drivers de esta emisora? El modelo desafía la selección con lo
  observado: "el margen histórico lo mueve el mix, no el volumen — ¿por qué tu
  build-up lo ignora?". Registrar resolución en thesis-journal.
- **Populate:** ¿cuál driver es el más frágil? ¿Dónde difieres del guidance y por
  qué? Si existe forecast-accuracy: confrontar el sesgo histórico.
