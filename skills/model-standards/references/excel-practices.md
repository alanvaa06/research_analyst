# Excel Best Practices (base CFI)

Convenciones obligatorias del modelo. Fuente: prácticas estándar de la industria
(CFI-based). `/model-check` audita contra esta lista.

## Estructura

- Separar inputs, cálculos y outputs en hojas o secciones claramente etiquetadas.
- Flujo top-to-bottom y left-to-right; periodos en columnas, líneas en filas.
- Un tab por módulo lógico (Assumptions, IS, BS, CF, Schedules, Valuation, Summary).
- Un archivo por modelo; evitar links entre libros (cero en este estándar).
- Cover sheet con propósito, versión, autor, fecha y leyenda de colores.

## Formato y colores

- Inputs hard-coded en fuente azul; fórmulas en negro; links a otras hojas en verde;
  links externos en rojo (y minimizados — aquí: prohibidos).
- Sombreado amarillo claro en celdas de input.
- Formato numérico consistente: comas, paréntesis para negativos, sin decimales en
  cifras enteras de moneda.
- Unidades (MXN mm, %, x) en encabezados de columna, no dentro de celdas.
- Freeze panes en primera columna de datos y fila de encabezado.

## Fórmulas

- Una fórmula por fila, copiada idéntica en todos los periodos.
- Jamás números hard-coded dentro de una fórmula; referenciar celda de input.
- Fórmulas cortas; lógica compleja en filas auxiliares.
- Evitar funciones volátiles (OFFSET, INDIRECT, NOW, TODAY) salvo necesidad real.
- INDEX/MATCH o XLOOKUP sobre VLOOKUP.
- IFERROR solo para errores esperados, nunca para ocultar errores reales.
- Anclas $ deliberadas; no abusar de referencias absolutas.
- SUMIFS/COUNTIFS sobre fórmulas de arreglo donde sea posible.

## Integridad y controles

- Balance check (Activos = Pasivos + Capital) en el header de cada hoja.
- Tie-out de flujo: caja final del CF = caja del BS.
- UNA celda de "Error check" en el cover que agrega cualquier quiebre del libro.
- Sin referencias circulares; si la circularidad interés-deuda es necesaria,
  controlarla con switch de iteración y documentarla.
- Nunca entregar un modelo en modo de cálculo manual.

## Sensibilidades y escenarios

- Escenarios desde UNA celda switch usando CHOOSE o INDEX.
- Todos los inputs de escenario centralizados en un bloque; no dispersos.
- Data tables para sensibilidades de dos variables; aisladas en tab dedicada.
- Stress con bull, base, bear; cada caso documentado.

## Legibilidad

- Etiquetas de fila descriptivas; sin abreviaturas crípticas.
- Subtotales indentados una columna; totales en negrita.
- Subrayado sobre subtotales; doble subrayado en totales finales.
- Agrupar (group/outline) filas de soporte para colapsar a vista resumen.
- Anchos de columna consistentes entre tabs.
- Gridlines ocultas en tabs de output y presentación.

## Performance

- Sin referencias de columna completa (A:A); rangos acotados o Tablas.
- Rangos grandes de datos → Excel Tables con referencias estructuradas.
- IFS/SWITCH o tablas de lookup sobre IFs anidados.
- Limpiar formato y formatos condicionales de rangos vacíos.

## Workflow

- Versionado con fecha `Model_YYYY-MM-DD_v#.xlsx`.
- Guardar template limpio antes de agregar overrides de escenario.
- Nunca borrar columnas a media serie; insertar nuevas al final de la serie temporal.
- Documentar todo supuesto no obvio con comentario de celda o fila de nota.

## Cuando el agente construye o edita el modelo

- Confirmar propósito, audiencia y horizonte ANTES de construir.
- Supuestos explícitos, en un solo bloque de inputs.
- Lógica de fórmulas explicada en lenguaje llano junto a cada bloque de cálculo.
- Correr balance check y tie-out ANTES de entregar — check rojo = reportar FALLA.
- Summary ejecutivo de una tab con los 3-5 outputs que importan.
