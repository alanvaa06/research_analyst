---
name: statement-mapper
description: Captura de estados financieros desde filings al modelo — extrae cada cifra con cita de fuente y página, la mapea a la línea estándar del model-spec, propone reclasificaciones, etiqueta guidance de management, y en modo ligero arma comp-snapshots de comparables. Usa esta skill siempre que haya que capturar históricos de un filing (10-K, 10-Q, reporte BMV), mapear un estado de resultados/balance/flujos al modelo, conciliar una línea contra la fuente, armar el snapshot de un comparable, o cuando el usuario diga "captura este trimestre", "mapea este PDF al modelo", "¿de dónde salió esta cifra?", "arma el snapshot de este comp".
---

# statement-mapper

Dueña única de la lectura de contenido de filings — de la emisora Y de comparables.
Su producto: cifras `observado` con cita exacta (documento, página/nota), mapeadas a
las líneas del `model-spec`. **No escribe en el xlsx** (entrega el mapeo a
model-standards) y **no mueve archivos** (eso es coverage-folders).

## Cuándo corre

- `/init-coverage` paso 3: captura de históricos (en paralelo con industry-analysis).
- `/update-quarter` paso 2: captura del trimestre nuevo.
- Modo ligero: comp snapshots, cuando industry-analysis entrega el universo.
- Standalone: capturar un solo estado, conciliar una línea, un snapshot suelto.

## Procedimiento — captura completa

1. Lee el filing desde `filings/` (la ruta la da coverage-folders).
2. Extrae estado por estado. **Cada cifra lleva: valor, documento, página o nota,
   fecha.** Cifra sin cita no existe.
3. Mapea a las líneas del model-spec. La presentación de la emisora rara vez coincide
   1:1 — propone el mapeo y las reclasificaciones como PROPUESTA, con el racional.
4. Gate: el usuario aprueba mapeo y reclasificaciones antes de entregar a
   model-standards. Las reclasificaciones aprobadas se registran en `journal/decisions.md`.
5. Etiquetado en la fuente: cifras de estados = `observado`; proyecciones, metas y
   rangos que da la administración (guidance del press release, del call, del MD&A)
   = `guidance` — NUNCA se capturan como observado. Doctrina: del management,
   priorizar lo cuantitativo verificable.
5b. **Transcripts obligatorios si existen:** si `transcripts/` tiene el
   transcript del periodo capturado, leerlo NO es opcional — extraer todo
   guidance cuantitativo (rangos, metas, capex/margen/tax guiado, color por
   segmento) etiquetado `guidance` con cita (transcript, sección/página). Es la
   fuente de guidance más rica del periodo; alimenta el contraste de
   driver-inventory y el triage.
6. Anti-doble-captura: verifica contra lo ya capturado antes de escribir.

## Procedimiento — comp snapshot (modo ligero)

1. Universo viene de `research/industry-report.md` (industry-analysis lo decide, no tú).
2. Por comparable: llena `templates/comp-snapshot.yaml` — balance e income items del
   último filing del comp con cita; market data (precio, acciones) de fuente pública
   con fuente y **timestamp** (`as_of` con hora: los precios envejecen).
3. Anota el marco contable del comp y las notas de comparabilidad (consulta la
   reference de framework-mapper si el marco difiere del de la emisora — pero la
   cita normativa la emite framework-mapper, no tú).
4. Sin fuente pública disponible para un campo ⇒ campo vacío y reportado; jamás
   estimar un dato de mercado.

## Reglas duras

- Cifra sin cita = no capturada. Sin excepciones, ni "es obvia".
- No corregir la aritmética de la emisora en silencio: si la suma del filing no
  cuadra, se reporta como hallazgo (posible input de impact-triage), no se "arregla".
- Períodos re-expresados o re-presentados por la emisora: capturar la versión más
  reciente y anotar la re-presentación en `journal/decisions.md`.

## Entrevista de cierre

Objetivo (adaptativa, per `templates/debate-protocol.md`): calidad de earnings.
¿Qué sorprendió de los históricos? ¿Qué línea merece desconfianza? Generar preguntas
desde lo capturado (ej. "cuentas por cobrar crecen 2× revenue tres trimestres
seguidos — ¿qué hipótesis tienes?"). Registrar en thesis-journal.
