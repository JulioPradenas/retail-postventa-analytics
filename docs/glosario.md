# Glosario — Retail Postventa Analytics

Definiciones de KPIs, métricas y términos usados en el proyecto. Para el *cómo*
y el *por qué* de cada cálculo, ver [`metricas_y_decisiones.md`](metricas_y_decisiones.md).

---

## 1. KPIs de negocio

### CPO — Contactos Por Orden
Número de contactos al servicio postventa dividido por el número de órdenes en
el mismo periodo. Es el **KPI central** del proyecto.

- **Fórmula:** `n_contactos / n_órdenes`
- **Interpretación:** CPO = 0.34 significa que ~1 de cada 3 órdenes genera un
  contacto. Cada contacto tiene un costo operativo (agente, tiempo, AHT).
- **Por qué importa:** bajar el CPO reduce costo de operación sin sacrificar
  servicio, atacando la *causa* del contacto (no atendiendo más rápido).
- **Mart:** `mart_cpo_semanal`, `mart_cpo_por_motivo`.

### OTD — On-Time Delivery (Entrega a Tiempo)
Porcentaje de despachos entregados en la fecha prometida o antes.

- **Fórmula:** `despachos_a_tiempo / despachos_totales`
- **Interpretación:** OTD = 90% significa que 1 de cada 10 pedidos llega tarde.
- **Por qué importa:** es el principal *driver* del CPO. Un pedido atrasado
  dispara la probabilidad de contacto (ver insight estrella).
- **Mart:** `mart_otd_vs_sla`.

### CSAT — Customer Satisfaction
Satisfacción del cliente tras un contacto atendido, en escala 1–5.

- **Fórmula:** `promedio(csat_score)` sobre contactos no abandonados.
- **Por qué importa:** mide la calidad percibida de la atención. CSAT bajo con
  CPO alto = doble problema (muchos contactos y mal resueltos).

### FCR — First Contact Resolution (Resolución al Primer Contacto)
Porcentaje de casos resueltos en el primer contacto, sin necesidad de recontacto.

- **Fórmula:** `resueltos_primer_contacto / contactos_no_abandonados`
- **Por qué importa:** FCR alto reduce recontactos → reduce CPO y sube CSAT.

---

## 2. Métricas operativas del contact center

| Término | Qué es | Cálculo |
|---|---|---|
| **AHT** (Average Handle Time) | Tiempo promedio de atención de un contacto | `promedio(aht_seconds)` en contactos no abandonados |
| **Tasa de abandono** | % de contactos que el cliente abandona antes de ser atendido | `abandonados / contactos_totales` |
| **Contacto abandonado** | Contacto sin atención de agente; tiene `agent_id`, `aht`, `csat`, `fcr` en NULL | flag `is_abandoned` |

---

## 3. Términos de logística y entrega

| Término | Definición |
|---|---|
| **SLA** (Service Level Agreement) | Promesa de entrega en días, según zona × modalidad. Ej: RM express = 1–2 días; regiones normal = 5–8 días. Define `promised_date`. |
| **`is_late`** | Booleano: el despacho llegó después de `promised_date`. |
| **`delay_days`** | Días de atraso cuando `is_late` es verdadero (`actual_delivery_date − promised_date`). |
| **`carrier`** | Empresa de transporte (Chilexpress, StarKen, DHL, Correos de Chile, Bluexpress). |
| **`carrier_modality`** | `express` o `normal` — distinta promesa de SLA. |
| **`zone`** | `RM` (Región Metropolitana) o `regions` (resto del país); afecta el SLA. |
| **`days_to_delivery`** | Días entre la orden y la entrega real (`actual_delivery_date − order_date`). |

---

## 4. Motivos (taxonomías de negocio)

- **Motivo de contacto** (`contact_motivo`): por qué el cliente contactó.
  10 categorías; ej: *Despacho tardío*, *Producto no llegó*, *Producto dañado*,
  *Consulta estado pedido*. Su distribución **cambia fuerte** entre órdenes a
  tiempo vs atrasadas (un atraso desplaza los motivos hacia *Despacho tardío* /
  *Producto no llegó*).
- **Motivo de devolución** (`return_motivo`): por qué se devolvió el producto.
  Permite separar devoluciones *prevenibles* (ligadas a atraso) de las
  inherentes al producto.

---

## 5. Términos de modelado de datos (dbt)

| Término | Definición |
|---|---|
| **Grain (granularidad)** | El nivel de detalle de una fila. Ej: `mart_cpo_semanal` tiene grain "una fila por semana". Definir el grain evita doble conteo. |
| **`stg_` (staging)** | Modelos que limpian y tipan el raw 1:1 (casts, renombres). Sin lógica de negocio. |
| **`dim_` (dimensión)** | Tablas descriptivas (clientes, carriers, productos) para filtrar/agrupar. |
| **`fct_` (hecho)** | Tablas de eventos medibles (órdenes, contactos) con sus métricas y claves. |
| **`mart_`** | Tablas finales agregadas que responden una pregunta de negocio y alimentan dashboards. |
| **`SAFE_DIVIDE`** | División de BigQuery que devuelve NULL en vez de error si el divisor es 0. Evita que el pipeline falle por una semana sin órdenes. |
| **`DATE_TRUNC(..., WEEK(MONDAY))`** | Agrupa fechas por semana calendario empezando el lunes. |

---

## 6. KPIs del modelo predictivo (M7)

| Término | Definición |
|---|---|
| **ROC-AUC** | Capacidad del modelo de distinguir órdenes que generarán contacto de las que no (0.5 = azar, 1.0 = perfecto). El modelo logra ~0.94. |
| **Precision / Recall** | Precision: de los predichos "con contacto", cuántos lo fueron. Recall: de los reales "con contacto", cuántos detectó. |
| **Data leakage** | Usar en el modelo información no disponible al momento de predecir. Se evita entrenando solo con features conocidas al momento del despacho. |
