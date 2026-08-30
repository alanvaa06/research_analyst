---
name: industry-analysis
description: Análisis de industria y mercado estilo CFA para una cobertura de equity — landscape competitivo, five forces de Porter, ciclo de vida de la industria, FODA, posicionamiento y universo de comparables; produce el reporte de industria que alimenta drivers, assumptions y tesis. Usa esta skill siempre que haya que analizar la industria de una emisora, mapear competidores, armar o refrescar un FODA, decidir el comp universe, evaluar posicionamiento competitivo o moats, o cuando el usuario diga "analiza la industria", "¿quiénes son los comparables?", "actualiza el landscape", "¿dónde compite esta emisora?".
---

# industry-analysis

Dueña única de `research/industry-report.md` y del universo de comparables. Es la etapa
top-down del proceso CFA: la tesis nace aquí, no en valuación. Los drivers de la
etapa siguiente se DERIVAN de la economía de industria que esta skill establece.

## Cuándo corre

- `/init-coverage` paso 4 (en paralelo con la captura de históricos).
- Standalone: refrescar el reporte cuando la industria se mueve (evento relevante
  sectorial, entrada de competidor, cambio regulatorio).

## Fuentes (sin APIs de pago — v1)

- Filings de la emisora Y de sus competidores (sección de negocio, MD&A, segmentos).
- Datos públicos (INEGI, reguladores sectoriales, cámaras) y web search de la
  plataforma si existe.
- `macro-view.yaml` para el contraste industria vs ciclo macro.
- **Etiquetado estricto:** hecho con fuente = `observado`; interpretación del
  analista (FODA, posicionamiento) = `supuesto`; lo que diga el management de
  cualquier emisora = `guidance`.

## Estructura de industry-report.md (marco CFA)

```markdown
# Industry Report — <industria> / <TICKER>   [fecha]

## 1. Estructura de la industria (five forces)
   Entrada · proveedores · compradores · sustitutos · rivalidad — cada fuerza con
   evidencia observada, no adjetivos.
## 2. Ciclo de vida y drivers de la industria
   embryonic|growth|mature|decline (alimenta life_cycle_stage del perfil) ·
   cíclica vs defensiva · sensibilidad a tasas/commodities/regulación/tecnología ·
   crecimiento del mercado vs PIB (insumo de la ruta top-down de revenue)
## 3. Landscape competitivo
   Tabla de competidores: participación (con fuente), marco contable, métricas
   comparables clave. De aquí sale el comp universe.
## 4. Posicionamiento de la emisora
   Moat (costo|marca|red|switching|IP) con evidencia · posición débil/media/fuerte
## 5. FODA
   Del ANALISTA (supuesto) — la skill estructura y desafía, no lo escribe por él
## 6. Universo de comparables
   Tickers seleccionados + selected_because por cada uno + quién quedó fuera y por qué
## 7. Supuestos de industria para el modelo
   Bloque que va a assumptions: crecimiento de mercado, participación, precios
   sectoriales — cada uno con fuente o marcado supuesto
```

## Contratos de salida

| Output | Consumidor |
|---|---|
| `industry-report.md` completo | analista; nota (etapa 7) |
| Universo de comparables (sección 6) | statement-mapper (snapshots) y Val_Comps |
| Bloque de supuestos de industria (sección 7) | driver-inventory → Assumptions |
| `life_cycle_stage` | issuer-profile (horizonte de forecast, peso de métodos) |
| Posicionamiento | impact-triage (materialidad depende de dónde compite) |

## Reglas duras

- Participaciones de mercado y tamaños SIEMPRE con fuente y fecha, o marcados
  `supuesto`. Un landscape sin fuentes es opinión con formato.
- El FODA es del analista: la skill propone estructura y evidencia, pregunta,
  desafía — el contenido final lo decide él.
- El comp universe es juicio del analista; la skill documenta el racional de cada
  inclusión Y de cada exclusión notable.

## Entrevista de cierre

Objetivo (adaptativa, per `templates/debate-protocol.md`): **¿dónde compite realmente
esta emisora y qué la protege?** El modelo desafía el FODA con lo observado en
filings de competidores (ej. "dices ventaja de costo; el competidor X reporta margen
bruto 400bps mayor — ¿cómo se sostiene tu F?"). Esta es la primera entrada
SUSTANTIVA del thesis-journal: la semilla de la tesis, con sus contra-argumentos.
