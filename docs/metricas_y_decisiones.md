# Métricas y decisiones — el *por qué* y el *cómo*

Este documento explica las decisiones analíticas del proyecto: de qué pregunta
de negocio parte, cómo se traduce en KPIs, cómo se calcula cada uno en SQL, y
por qué se tomó cada decisión de diseño. Para definiciones cortas ver
[`glosario.md`](glosario.md); para el hallazgo ver [`insights.md`](insights.md).

---

## 1. La pregunta de negocio

> ¿Cuántos contactos genera cada orden de e-commerce, por qué motivos, y cómo
> podemos predecir y reducir los contactos evitables?

Se descompone en cuatro sub-preguntas, cada una con un mart que la responde:

| Sub-pregunta | KPI | Mart |
|---|---|---|
| ¿Cuántos contactos por orden? | CPO | `mart_cpo_semanal` |
| ¿Por qué contactan? | Mix de motivos | `mart_cpo_por_motivo` |
| ¿Cumplimos la promesa de entrega? | OTD | `mart_otd_vs_sla` |
| ¿Cuánto sube el CPO cuando baja el OTD? | Correlación OTD↔CPO | `mart_correlacion_otd_cpo` |

La cadena lógica del proyecto: **mal OTD → más contactos → más CPO → más costo**.
Por eso el OTD es la palanca, y el CPO el resultado.

---

## 2. Cómo se calcula cada KPI (decisiones de SQL)

### 2.1 CPO — `mart_cpo_semanal`

```sql
ROUND(SAFE_DIVIDE(COALESCE(c.n_contacts, 0), o.n_orders), 4) AS cpo
```

**Decisiones:**
- **`SAFE_DIVIDE`** en vez de `/`: si una semana no tiene órdenes, devuelve NULL
  en lugar de tumbar el modelo con un error de división por cero.
- **`COALESCE(n_contacts, 0)`**: una semana con órdenes pero sin contactos debe
  dar CPO = 0, no NULL. El `LEFT JOIN` desde órdenes garantiza que toda semana
  con actividad aparezca aunque no haya contactos.
- **Grain semanal con `WEEK(MONDAY)`**: la semana es la unidad de seguimiento
  operativo natural; el lunes como inicio alinea con el calendario laboral.

### 2.2 OTD — `mart_otd_vs_sla`

```sql
ROUND(SAFE_DIVIDE(COUNTIF(NOT is_late), COUNT(*)), 4) AS otd_rate
```

**Decisiones:**
- **`COUNTIF(NOT is_late)`**: OTD se define en positivo (entregas a tiempo /
  total), que es como lo lee el negocio ("cumplimos el 90%").
- **Grain por `carrier × zone`**: el OTD no es uniforme — varía por transportista
  y por zona. Agrupar así permite accionar sobre el carrier correcto en vez de
  mirar un promedio que esconde el problema.
- **`avg_delay_days_when_late`**: no basta saber *cuántos* llegan tarde, sino
  *cuánto* tarde. Un atraso de 1 día no es lo mismo que uno de 5.

### 2.3 Insight estrella — `mart_correlacion_otd_cpo`

El cálculo clave del proyecto. La sutileza está en **unir a nivel de orden antes
de agregar**, para evitar el desfase de fechas (un contacto ocurre días después
de la orden):

```sql
order_contacts AS (
    SELECT o.order_id, o.order_date, o.is_late,
           IF(c.order_id IS NOT NULL, 1, 0) AS has_contact
    FROM fct_orders o
    LEFT JOIN (SELECT DISTINCT order_id FROM fct_contacts) c
      ON o.order_id = c.order_id
)
```

**Decisiones:**
- **Unir por `order_id`, no por fecha**: si se cruzaran contactos y órdenes por
  semana, una orden de fin de mes con contacto en el mes siguiente quedaría
  descuadrada. Atar el contacto a su orden y *luego* agregar por
  `order_date` resuelve el desfase.
- **`SELECT DISTINCT order_id`**: una orden puede generar varios contactos; para
  la *tasa de contacto* solo importa si tuvo ≥1, no cuántos.
- **Bucketing de OTD** (`>=90%`, `80–90%`, `<80%`): convierte una variable
  continua en tramos accionables que el negocio entiende y sobre los que se fijan
  umbrales de alerta.

**Hallazgo:** órdenes atrasadas contactan ~67% vs ~29% las puntuales (2.4×).

### 2.4 KPIs del contact center — `mart_kpis_contact_center`

```sql
COUNTIF(is_abandoned) / COUNT(*)                              AS abandon_rate,
AVG(CASE WHEN NOT is_abandoned THEN aht_seconds END)          AS avg_aht_seconds,
COUNTIF(NOT is_abandoned AND fcr) / COUNTIF(NOT is_abandoned) AS fcr_rate,
AVG(CASE WHEN NOT is_abandoned THEN csat_score END)           AS avg_csat
```

**Decisión transversal — excluir abandonados de AHT/FCR/CSAT:** un contacto
abandonado no tuvo agente, así que no tiene tiempo de atención, ni resolución, ni
satisfacción. Incluirlos con valor 0 contaminaría los promedios. Por eso el
denominador de FCR y los promedios de AHT/CSAT usan solo `NOT is_abandoned`,
mientras que `abandon_rate` sí usa el total (su numerador *son* los abandonados).

---

## 3. Umbrales y alertas — `mart_alerts_diarias`

Los KPIs sin umbral no accionan. Este mart define niveles de prioridad y dueño:

| KPI | P2 (alerta) | P1 (crítico) | Owner |
|---|---|---|---|
| OTD | < 90% | < 80% | Logística (P2) / Operaciones (P1) |
| Tasa de abandono | > 20% | > 25% | Contact Center |
| CSAT | < 3.0 | < 2.5 | Contact Center |

**Decisiones:**
- **Grain diario** (no semanal): una alerta debe dispararse *hoy*, no esperar al
  cierre de semana. Operación necesita reaccionar rápido.
- **`FULL OUTER JOIN` entre OTD y contact center**: un día puede tener problema de
  OTD sin problema de contact center (o viceversa). El full join asegura no
  perder ninguna fecha con alerta de cualquiera de los dos lados.
- **`WHERE` final**: el mart solo muestra días *con* alerta activa — es una bandeja
  de excepciones, no un reporte de todo.
- **Owner por KPI**: cada alerta sale con responsable, para que sea accionable y
  no solo informativa.

---

## 4. Del KPI al OKR (capa estratégica)

Los KPIs miden; los OKR fijan ambición. Ejemplo de cómo el proyecto se traduce a
un OKR trimestral (framing ilustrativo sobre las métricas reales):

> **Objetivo:** Reducir los contactos postventa evitables sin sacrificar servicio.
>
> - **KR1:** Subir el OTD global de 85.8% → 92%.
> - **KR2:** Bajar el CPO de 0.34 → 0.28 (≈800 contactos evitables/año a escala 10K).
> - **KR3:** Mantener CSAT ≥ 3.5 y FCR ≥ 70% durante la reducción.

La relación entre KR1 y KR2 **no es supuesta, está medida**: el
`mart_correlacion_otd_cpo` cuantifica que cada punto de mejora en OTD baja el CPO
en ~0.04. Eso convierte el OKR en una hipótesis con respaldo en datos, no en un
número aspiracional al aire.

---

## 5. Decisiones de arquitectura analítica (resumen)

| Decisión | Por qué |
|---|---|
| Capas `stg → dim/fct → mart` | Separar limpieza, modelado y agregación; cada capa testeable por separado. |
| `fct_orders` con grain 1 orden = 1 despacho | Une orden y envío en la tabla central; toda métrica de OTD y CPO parte de aquí. |
| `fct_contacts` con contexto de orden y envío | Permite cruzar contacto ↔ atraso sin re-joins en cada mart. |
| `SAFE_DIVIDE` en todos los ratios | Robustez: ninguna métrica tumba el pipeline por divisor 0. |
| Catálogos y probabilidades en `config/settings.py` | Fuente única de verdad del dominio (carriers, SLA, tasas); reproducibilidad. |
| Cada modelo con tests (`unique`, `not_null`, `relationships`) | Calidad como barrera: `dbt test` frena el pipeline antes de contaminar dashboards o el modelo ML. |

Las probabilidades sintéticas en `config/settings.py` están calibradas para que
los datos reproduzcan el comportamiento real esperado: `CONTACT_PROB_ON_TIME =
0.27` y `CONTACT_PROB_LATE = 0.70` generan justamente la brecha 2.4× del insight
estrella, y el promedio ponderado (~0.335) fija el CPO global en ~0.34.
