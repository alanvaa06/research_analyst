# Integrity Checks — la lista que corre /model-check

Cada check es determinista: fórmula en la tab `Checks` o escaneo por código (openpyxl).
La celda de error del Cover agrega TODOS. Un check rojo = el comando reporta FALLA,
nunca éxito. Orden: primero estructura, luego contabilidad, luego contenido.

## Estructurales (escaneo por código)

| # | Check | Cómo |
|---|---|---|
| S1 | Todas las tabs del model-spec presentes; schedules del driver-map existen | openpyxl: nombres de hoja vs contrato |
| S2 | Cero links externos a otros libros | escaneo de fórmulas por `[` |
| S3 | Sin funciones volátiles (OFFSET, INDIRECT, NOW, TODAY) | escaneo de fórmulas |
| S4 | Sin números hard-coded dentro de fórmulas (fuera de Assumptions) | escaneo: constantes en fórmulas de tabs de cálculo |
| S5 | Una fórmula por fila: fórmula idéntica (relativa) en todos los periodos | comparación de R1C1 por fila |
| S6 | Inputs solo en Assumptions; tabs de cálculo sin celdas constantes sin etiqueta | escaneo por tab |
| S7 | Modo de cálculo automático, no manual | propiedad del libro |
| S8 | Versionado del archivo cumple `_YYYY-MM-DD_v#` | nombre de archivo |

## Contables (fórmulas en tab Checks)

| # | Check | Fórmula |
|---|---|---|
| C1 | Balance cuadra cada periodo | A − (P + C) = 0, todos los periodos |
| C2 | Tie-out de caja | caja final CF = caja BS, todos los periodos |
| C3 | Roll de utilidades retenidas | RE₁ = RE₀ + NI − dividendos |
| C4 | Depreciación acumulada consistente con schedule | BS vs Sch_PPE |
| C5 | Interés consistente con schedule de deuda | IS vs Sch_Debt (documentar switch si hay circularidad) |

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

## Reporte de /model-check

```
[ok] / [x] por check, agrupado S / C / D
Resumen: N ok, M fallas, K avisos
Falla => exit report "FALLA", lista de celdas/hojas afectadas, siguiente acción sugerida
```
