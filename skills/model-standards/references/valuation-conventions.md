# Valuation Conventions — menú de métodos y pestañas deterministas

Doctrina: **el modelo arma la estructura y las fórmulas; el analista pone cada
supuesto; nada se calcula por generación libre.** Usuario en el loop en cada supuesto.
El football field agrega SOLO métodos activos en `issuer-profile.yaml`.

## Menú y activación

| Activación | Método | Supuestos del analista |
|---|---|---|
| **Core — siempre** | DCF FCFF multi-stage, terminal DUAL | WACC (componentes), g terminal, múltiplo de salida, horizonte |
| **Core — siempre** | Comps (EV/EBITDA, P/E, P/B, EV/Sales) | universo (viene de industry-analysis), múltiplo aplicable |
| **Core — siempre** | Sensibilidades (data tables 2 vars) + football field | rangos de sensibilidad |
| Dividendera estable | DDM: Gordon / two-stage / H-model | g por etapa, payout |
| Apalancamiento estable | FCFE directo | r equity, trayectoria de deuda neta |
| FIBRA / REIT | NAV + FFO/AFFO | cap rate, ajustes AFFO — convención local FIBRA [VERIFICAR] |
| Conglomerado | SOTP | método por segmento, descuento de holding |
| Banco (v2) | Residual income + justified P/B | r, ω persistencia — **especificado, INACTIVO v1** |

## Convenciones por pestaña

### Val_DCF (FCFF multi-stage)
- FCFF derivado por fórmula desde el modelo (EBIT×(1−t) + D&A − CapEx − ΔWC), nunca
  re-tecleado.
- WACC: componentes visibles — rf de `Macro` (macro-view), ERP de `Macro`, beta
  (supuesto con fuente), costo de deuda, pesos a mercado. Cada uno etiquetado.
- **Terminal dual obligatorio:** Gordon (g) Y exit multiple, lado a lado.
  Cruce: Gordon ⇒ múltiplo implícito; exit multiple ⇒ g implícita. Ambos visibles.
  Divergencia grande = check D4: revisar supuesto con el analista, no promediar.
- Etapas: single-stage es el caso degenerado; default 2-3 etapas según
  `life_cycle_stage` (growth ⇒ horizonte largo).
- **Bloque beta pure-play (Hamada)** — mecánica visible, no "beta con fuente" a secas:
  - β_u por comp = β_l / (1 + (1−t)·D/E) — una fila por comp; β_l input `observado`
    con fuente en comentario; D y E del `comps/*.yaml`.
  - β_u grupo = mediana; β_relevered = β_u grupo × (1 + (1−t)·D/E objetivo).
  - D/E objetivo: `supuesto` del analista en Assumptions. El analista puede
    sobreescribir el beta final (documentado en journal/decisions.md); la mecánica
    queda visible como referencia.
- **Bloque reverse DCF (expectativas implícitas)** — forma cerrada, sin Goal Seek:
  - EV de mercado = mkt cap actual + deuda neta + minoritarios + preferentes.
  - TV implícita = (EV − PV de FCFF explícitos) × (1+WACC)^n.
  - g implícita = WACC − FCFF_{n+1} / TV implícita.
  - Tercera columna junto al cruce de terminales: "el mercado descuenta g = X; tú
    supones g = Y" (check D4b — debate, nunca bloqueo).

### Val_Comps
- Múltiplos calculados POR FÓRMULA desde `comps/*.yaml`: EV = mkt cap + deuda − caja
  + minoritarios + preferentes; cada componente del snapshot, con fuente.
- Promedio del grupo: **media armónica** (doctrina CFA para múltiplos), mediana como
  referencia; nunca media aritmética sola.
- Staleness: `as_of` de cada snapshot flaggeado si viejo (check D3).
- Comparabilidad entre marcos: EBITDA IFRS 16 vs ASC 842 NO comparable directo —
  fila de ajuste de arrendamientos cuando el universo mezcla marcos (ver
  framework-mapper reference).
- **Bloque de múltiplos justificados + PVGO** (debajo del grupo de comps) — cero
  inputs nuevos, todo por referencia a b, g, r, ROE ya existentes en
  Assumptions/Val_DCF/Ratios:
  - P/E justificado leading = (1−b)/(r−g); trailing = (1−b)(1+g)/(r−g).
  - P/B justificado = (ROE−g)/(r−g); P/S justificado = (E₀/S₀)(1−b)(1+g)/(r−g).
  - PVGO = P₀ − E₁/r, y PVGO/P₀ (% del precio que es expectativa de crecimiento).
  - Lectura por fila: múltiplo de mercado vs justificado — de descriptivo ("a
    cuánto cotizan") a normativo ("a cuánto deberían").

### Val_DDM (condicional)
- Gordon: V₀ = D₁/(r−g). Two-stage y H-model con etapas explícitas.
- Consistencia: g = ROE × (1−payout) visible como check suave.

### Val_NAV_AFFO (condicional — FIBRAs)
- FFO = NI + D&A inmobiliaria ± partidas no recurrentes; AFFO = FFO − capex de
  mantenimiento − comisiones lineales. Convención local de ajustes FIBRA:
  [VERIFICAR — contribución bienvenida].
- NAV: cap rate del analista sobre NOI forward; sensibilidad cap rate obligatoria.

### Val_SOTP (condicional)
- Un bloque por segmento (segmentos del issuer-profile); método por segmento
  elegido por el analista; descuento de holding como supuesto explícito, no
  escondido en el múltiplo.

### Val_RI (v2 — inactivo)
- Especificación: V₀ = B₀ + Σ RI descontado; RI = (ROE − r) × B; justified
  P/B = (ROE − g)/(r − g); continuing RI con ω.
- Exige clean surplus — verificar antes de activar. Se activa cuando el mapeo
  Anexo 33 (bancos) entre al alcance.

### Sensitivity + Summary
- Data tables aisladas; variables típicas: WACC × g, cap rate × NOI, múltiplo × EBITDA.
- Football field: rango por método activo, precio actual como línea, precio objetivo
  del analista marcado — el precio objetivo es SUPUESTO del analista informado por
  los métodos, jamás un promedio automático.

## Principio de convergencia (check D5)

DDM, FCFE y RI convergen bajo supuestos idénticos. Divergencia extrema entre métodos
activos = supuesto inconsistente entre pestañas (g, payout, ROE, r). El modelo la
reporta y el debate la discute; nunca se resuelve promediando.
