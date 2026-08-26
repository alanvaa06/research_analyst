---
name: coverage-folders
description: Estructura de carpetas y archivado de filings SEC/BMV para una cobertura de equity — instancia el árbol estándar por emisora, aplica la convención de nombres, detecta filings faltantes y archiva documentos nuevos (10-K, 10-Q, 8-K, reportes BMV, eventos relevantes). Usa esta skill siempre que haya que crear la estructura de una cobertura nueva, archivar o renombrar un filing, organizar documentos de una emisora, o cuando el usuario diga "archiva este 10-Q", "organiza estos filings", "crea la carpeta de la emisora", "¿qué documentos me faltan?".
---

# coverage-folders

Dueña única del árbol de carpetas, el naming y el archivado. **Nunca lee el contenido
de los filings** (eso es de statement-mapper) — clasifica por tipo de documento y
metadatos, mueve y renombra. Las demás skills solo leen rutas.

## Cuándo corre

- `/init-coverage` paso 1: instanciar el árbol.
- `/update-quarter` paso 1: archivar el filing nuevo.
- Standalone: "archiva este 10-Q de AMX", "¿qué falta en mi carpeta?".

## Procedimiento — setup

1. Instancia el árbol de `templates/coverage-tree.md` bajo `workspace/<TICKER>/`.
   Colisión con cobertura existente ⇒ preguntar; NUNCA sobrescribir.
2. Clasifica los archivos sueltos que el usuario entregó: tipo (10-K/10-Q/8-K/
   BMV-annual/BMV-quarterly/evento relevante), periodo, y renombra según la
   convención (`<TICKER>_<tipo>_<periodo>[_fecha].<ext>`). Ambigüedad ⇒ preguntar.
3. Checklist de faltantes contra el mínimo del pipeline: último anual + trimestrales
   del año en curso. Reporta encontrado / faltante — no bloquea, informa.
4. Verifica que `workspace/macro-view.yaml` existe (si no: crear desde template,
   vacío, y avisar).

## Procedimiento — archivado (mantenimiento)

1. Identifica tipo y periodo del documento nuevo.
2. Anti-duplicado: ¿ya existe ese periodo? Corrección de la emisora ⇒ conservar
   ambos, nuevo con sufijo `_amended`.
3. Renombra, coloca, reporta ruta final.

## Reglas duras

- **Nada se borra, jamás.** Retención mínima 7 años (Standard V(C)). "Limpiar la
  carpeta" = reorganizar, nunca eliminar.
- Un archivo = un documento. Sin copias "final_v2".
- Esta skill no abre PDFs para leer estados financieros; si el usuario pide extraer
  cifras, eso es statement-mapper.

## Entrevista de cierre (solo en setup de cobertura nueva)

Objetivo (adaptativa, per `templates/debate-protocol.md`): sesgo de entrada. ¿Por qué
esta emisora? ¿Qué esperas encontrar? ¿Qué opinión traes ANTES de ver los números?
Primera entrada del thesis-journal — el valor está en documentar el prior para poder
contrastarlo después.
