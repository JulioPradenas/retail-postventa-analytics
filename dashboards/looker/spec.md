# Looker Studio — Especificación Completa del Dashboard
## Retail Postventa Analytics 2024

**Proyecto GCP:** `project-5089395c-793b-4923-a0d`
**Cuenta:** `prad3nas@gmail.com`
**URL:** https://lookerstudio.google.com

---

## 1. Configuración inicial del informe

### 1.1 Crear el informe

1. Ir a https://lookerstudio.google.com → **Crear → Informe en blanco**
2. En el modal "Añadir datos a este informe", cerrar por ahora (clic en X)
3. En la barra superior: **Recurso → Gestionar fuentes de datos añadidas → Añadir una fuente de datos**

### 1.2 Agregar las 7 fuentes de datos (una por mart)

Para cada mart, repetir: **Añadir datos → BigQuery → Mi proyecto → Mis proyectos**

| Alias en el informe | Proyecto | Dataset | Tabla |
|---|---|---|---|
| `CPO Semanal` | `project-5089395c-793b-4923-a0d` | `retail_postventa_marts` | `mart_cpo_semanal` |
| `CPO por Motivo` | `project-5089395c-793b-4923-a0d` | `retail_postventa_marts` | `mart_cpo_por_motivo` |
| `OTD vs SLA` | `project-5089395c-793b-4923-a0d` | `retail_postventa_marts` | `mart_otd_vs_sla` |
| `Correlación OTD-CPO` | `project-5089395c-793b-4923-a0d` | `retail_postventa_marts` | `mart_correlacion_otd_cpo` |
| `KPIs Contact Center` | `project-5089395c-793b-4923-a0d` | `retail_postventa_marts` | `mart_kpis_contact_center` |
| `Alertas Diarias` | `project-5089395c-793b-4923-a0d` | `retail_postventa_marts` | `mart_alerts_diarias` |
| `Devoluciones Motivo` | `project-5089395c-793b-4923-a0d` | `retail_postventa_marts` | `mart_devoluciones_motivo` |

### 1.3 Campos calculados a crear en la fuente `CPO Semanal`

Ir a **Recurso → Gestionar fuentes de datos → CPO Semanal → Editar → Añadir campo**

| Nombre del campo | Fórmula | Tipo |
|---|---|---|
| `cpo_pct` | `cpo * 100` | Número (2 dec.) |
| `semana_label` | `FORMAT_DATETIME("%d %b", week_start)` | Texto |

### 1.4 Campos calculados en `KPIs Contact Center`

| Nombre del campo | Fórmula | Tipo |
|---|---|---|
| `aht_minutos` | `avg_aht_seconds / 60` | Número (1 dec.) |
| `abandon_pct` | `abandon_rate * 100` | Número (1 dec.) |
| `fcr_pct` | `fcr_rate * 100` | Número (1 dec.) |

### 1.5 Configuración visual global

- Tema: **Moderno** (Panel → Tema y diseño → Moderno)
- Fuente de texto: **Roboto**
- Colores primarios: `#1A73E8` (azul), `#EA4335` (rojo alerta), `#34A853` (verde OK), `#FBBC04` (amarillo P2)
- Fondo del informe: `#F8F9FA`
- Tamaño del lienzo: **1600 × 900 px**

---

## 2. Página 1: Resumen Ejecutivo

**Nombre de página:** `Resumen Ejecutivo`
**Propósito:** Vista de alto nivel para gerencia. KPIs globales + tendencia semanal.

### 2.1 Header

- **Cuadro de texto** (ancho: 1600px, alto: 60px, fondo: `#1A73E8`)
  - Texto: `Retail Postventa Analytics — Resumen 2024`
  - Color texto: blanco, tamaño: 20px, negrita

### 2.2 Control de fecha

- **Insertar → Control → Rango de fechas**
- Posición: top-right del canvas
- Fuente de datos: `CPO Semanal`
- Campo de fecha: `week_start`
- Valor por defecto: Todo el período (Jan 2024 – Dec 2024)

### 2.3 Scorecards (fila superior, 4 tarjetas iguales, ancho ~360px c/u)

**Scorecard 1 — CPO promedio**
- Fuente: `CPO Semanal`
- Métrica: `cpo` → agregación: **Promedio**
- Etiqueta: `CPO Promedio`
- Formato: número, 3 decimales
- Color de comparación: referencia = 0.35 (verde si menor, rojo si mayor)

**Scorecard 2 — OTD global**
- Fuente: `OTD vs SLA`
- Métrica: `otd_rate` → agregación: **Promedio**
- Etiqueta: `OTD Global`
- Formato: porcentaje, 1 decimal
- Color de comparación: referencia = 90% (verde si mayor, rojo si menor)

**Scorecard 3 — Total contactos**
- Fuente: `CPO Semanal`
- Métrica: `n_contacts` → agregación: **Suma**
- Etiqueta: `Contactos Totales`
- Formato: entero con separador de miles

**Scorecard 4 — Total órdenes**
- Fuente: `CPO Semanal`
- Métrica: `n_orders` → agregación: **Suma**
- Etiqueta: `Órdenes Totales`
- Formato: entero con separador de miles

### 2.4 Gráfico de línea: Evolución CPO semanal

- Tipo: **Gráfico de series temporales**
- Fuente: `CPO Semanal`
- Dimensión: `week_start` (granularidad: semana)
- Métrica 1: `cpo` (color: `#1A73E8`, nombre: "CPO")
- Línea de referencia: valor fijo = 0.35, color `#EA4335`, etiqueta "Target"
- Eje Y: mínimo 0, máximo 1.0
- Título: `Contactos por Orden (CPO) — Evolución Semanal`
- Tamaño: ~900px × 300px

### 2.5 Gráfico de barras: OTD por carrier

- Tipo: **Gráfico de barras**
- Fuente: `OTD vs SLA`
- Dimensión: `carrier`
- Desglose: `zone`
- Métrica: `otd_rate`
- Ordenar por: `otd_rate` ascendente
- Formato métrica: porcentaje, 1 decimal
- Línea de referencia: 0.90 (color rojo)
- Título: `On-Time Delivery por Carrier y Zona`
- Tamaño: ~600px × 300px

---

## 3. Página 2: Insight OTD ↔ CPO ⭐

**Nombre de página:** `Impacto del Atraso`
**Propósito:** Demostrar el insight estrella — los atrasos generan el 67% de contactos.

### 3.1 Header de página

- Cuadro de texto (fondo `#34A853`, texto blanco):
  `⭐ Insight: Las órdenes atrasadas generan contacto 2.4× más que las en tiempo`

### 3.2 Scorecards comparativos (2 columnas)

**Scorecard — CPO semanas buenas (OTD ≥ 90%)**
- Fuente: `Correlación OTD-CPO`
- Filtro interno: `otd_bucket = "OTD >= 90%"`
- Métrica: `cpo` → Promedio
- Etiqueta: `CPO cuando OTD ≥ 90%`
- Fondo: `#34A853` (verde)

**Scorecard — CPO semanas malas (OTD < 90%)**
- Fuente: `Correlación OTD-CPO`
- Filtro interno: `otd_bucket ≠ "OTD >= 90%"`
- Métrica: `cpo` → Promedio
- Etiqueta: `CPO cuando OTD < 90%`
- Fondo: `#EA4335` (rojo)

**Scorecard — Tasa de atraso global**
- Fuente: `OTD vs SLA`
- Métrica: calculado = `SUM(n_late) / SUM(n_shipments)`
- Etiqueta: `% Órdenes con Atraso`
- Formato: porcentaje, 1 decimal

### 3.3 Gráfico de dispersión: OTD vs CPO por semana

- Tipo: **Gráfico de dispersión**
- Fuente: `Correlación OTD-CPO`
- Dimensión: `week_start`
- Métrica eje X: `otd_rate`
- Métrica eje Y: `cpo`
- Tamaño burbuja: `n_orders`
- Color por: `otd_bucket`
  - `OTD >= 90%` → `#34A853`
  - `OTD 80-90%` → `#FBBC04`
  - `OTD < 80%` → `#EA4335`
- Etiqueta en ejes:
  - X: `OTD Rate (% entregas en tiempo)`
  - Y: `CPO (contactos por orden)`
- Título: `Relación OTD ↔ CPO por semana (2024)`
- Tamaño: ~700px × 380px

### 3.4 Gráfico de barras: Motivos de contacto

- Tipo: **Gráfico de barras horizontales**
- Fuente: `CPO por Motivo`
- Dimensión: `contact_motivo`
- Métrica 1: `n_contacts` (barra principal)
- Métrica 2: `pct_of_contacts` (etiqueta en la barra, formato %)
- Ordenar por: `n_contacts` descendente
- Título: `Top Motivos de Contacto Postventa`
- Tamaño: ~780px × 380px

---

## 4. Página 3: Contact Center KPIs

**Nombre de página:** `Contact Center`
**Propósito:** KPIs operativos semanales del equipo de atención.

### 4.1 Scorecards globales (período completo)

**Scorecard — Abandon Rate**
- Fuente: `KPIs Contact Center`
- Métrica: `abandon_pct` (campo calculado) → Promedio
- Etiqueta: `Abandon Rate`
- Formato: porcentaje, 1 decimal
- Referencia: 15% (verde si menor)

**Scorecard — FCR Rate**
- Fuente: `KPIs Contact Center`
- Métrica: `fcr_pct` → Promedio
- Etiqueta: `First Contact Resolution`
- Formato: porcentaje, 1 decimal
- Referencia: 68% (verde si mayor)

**Scorecard — AHT Promedio**
- Fuente: `KPIs Contact Center`
- Métrica: `aht_minutos` → Promedio
- Etiqueta: `AHT (minutos)`
- Formato: número, 1 decimal

**Scorecard — CSAT Promedio**
- Fuente: `KPIs Contact Center`
- Métrica: `avg_csat` → Promedio
- Etiqueta: `CSAT Promedio`
- Formato: número, 2 decimales
- Referencia: 3.5 (verde si mayor)

### 4.2 Gráfico de líneas múltiples: KPIs semanales

- Tipo: **Gráfico de series temporales**
- Fuente: `KPIs Contact Center`
- Dimensión: `week_start`
- Métricas:
  - `fcr_pct` (color `#34A853`, nombre "FCR %")
  - `abandon_pct` (color `#EA4335`, nombre "Abandon %")
- Eje Y izquierdo: 0–100 (%)
- Título: `FCR vs Abandon Rate — Evolución Semanal`
- Tamaño: ~900px × 280px

### 4.3 Gráfico de línea: CSAT semanal

- Tipo: **Gráfico de series temporales**
- Fuente: `KPIs Contact Center`
- Dimensión: `week_start`
- Métrica: `avg_csat` (color `#1A73E8`)
- Línea de referencia: 3.5
- Eje Y: 1–5
- Título: `CSAT Promedio Semanal`
- Tamaño: ~600px × 250px

### 4.4 Tabla: Detalle semanal

- Tipo: **Tabla**
- Fuente: `KPIs Contact Center`
- Dimensión: `week_start`
- Métricas: `n_contacts_total`, `n_abandoned`, `abandon_pct`, `avg_aht_seconds`, `fcr_pct`, `avg_csat`
- Ordenar por: `week_start` descendente
- Paginación: 15 filas
- Formato condicional en `abandon_pct`: rojo si > 20%, amarillo si > 15%

---

## 5. Página 4: Devoluciones

**Nombre de página:** `Devoluciones`
**Propósito:** Identificar motivos de devolución y su relación con atrasos.

### 5.1 Scorecards

**Scorecard — Total devoluciones**
- Fuente: `Devoluciones Motivo`
- Métrica: `n_returns` → Suma
- Etiqueta: `Total Devoluciones`

**Scorecard — Tasa de devolución**
- Fuente: `Devoluciones Motivo`
- Métrica: `n_returns` → Suma → expresión: `/ 10000`
- Etiqueta: `Tasa de Devolución`
- Formato: porcentaje, 1 decimal

**Scorecard — % relacionadas con atraso**
- Fuente: `Devoluciones Motivo`
- Métrica: calculado = `SUM(n_late_related) / SUM(n_returns)`
- Etiqueta: `% Relacionadas con Atraso`
- Formato: porcentaje, 1 decimal

### 5.2 Gráfico de torta: Devoluciones por motivo

- Tipo: **Gráfico de anillo**
- Fuente: `Devoluciones Motivo`
- Dimensión: `return_motivo`
- Métrica: `n_returns`
- Mostrar etiqueta con porcentaje
- Tamaño: ~450px × 380px

### 5.3 Gráfico de barras apiladas: Atrasos vs total

- Tipo: **Gráfico de barras**
- Fuente: `Devoluciones Motivo`
- Dimensión: `return_motivo`
- Métrica 1: `n_late_related` (nombre "Relacionadas con atraso", color `#EA4335`)
- Métrica 2: calculado = `n_returns - n_late_related` (nombre "Sin relación con atraso", color `#9AA0A6`)
- Barras apiladas al 100%
- Título: `% Devoluciones Relacionadas con Atraso por Motivo`
- Tamaño: ~700px × 380px

### 5.4 Tabla detallada

- Tipo: **Tabla con mapa de calor**
- Fuente: `Devoluciones Motivo`
- Dimensión: `return_motivo`
- Métricas: `n_returns`, `pct_of_returns`, `n_late_related`, `pct_late_related`
- Mapa de calor en `pct_late_related` (más intenso = mayor relación con atraso)

---

## 6. Página 5: Alertas Operativas

**Nombre de página:** `Alertas`
**Propósito:** Monitoreo diario de KPIs fuera de rango.

### 6.1 Scorecards de resumen

**Scorecard — Días con alerta P1**
- Fuente: `Alertas Diarias`
- Tipo: Tabla → contar filas donde `otd_alert = "P1"` OR `abandon_alert = "P1"`
- Alternativa: crear campo calculado `es_p1 = IF(otd_alert = "P1" OR abandon_alert = "P1" OR csat_alert = "P1", 1, 0)`
- Etiqueta: `Días con Alerta P1`
- Fondo: `#EA4335` si valor > 0

**Scorecard — Días con alerta P2**
- Similar con `"P2"`
- Fondo: `#FBBC04` si valor > 0

### 6.2 Tabla de alertas (componente principal)

- Tipo: **Tabla**
- Fuente: `Alertas Diarias`
- Dimensiones/Métricas:

| Columna | Campo | Formato |
|---------|-------|---------|
| Fecha | `metric_date` | dd/MM/yyyy |
| OTD | `otd_rate` | % 1 dec. |
| Alerta OTD | `otd_alert` | texto |
| Owner OTD | `otd_owner` | texto |
| Abandon | `abandon_rate` | % 1 dec. |
| Alerta Abandono | `abandon_alert` | texto |
| Owner Abandono | `abandon_owner` | texto |
| CSAT | `avg_csat` | número 2 dec. |
| Alerta CSAT | `csat_alert` | texto |

- Ordenar: `metric_date` descendente
- Paginación: 20 filas
- Formato condicional:
  - Celda `otd_alert` = "P1" → fondo rojo, texto blanco
  - Celda `otd_alert` = "P2" → fondo amarillo
  - Celda `abandon_alert` = "P1" → fondo rojo
  - Celda `abandon_alert` = "P2" → fondo amarillo
  - Celda `csat_alert` = "P1" → fondo rojo

### 6.3 Gráfico de línea: OTD diario con umbrales

- Tipo: **Gráfico de series temporales**
- Fuente: `Alertas Diarias`
- Dimensión: `metric_date`
- Métrica: `otd_rate`
- Líneas de referencia:
  - 0.90 (color rojo, etiqueta "Umbral P2")
  - 0.80 (color `#EA4335` oscuro, etiqueta "Umbral P1")
- Título: `OTD Diario — Días con Alertas Activas`
- Nota: este mart solo incluye días con al menos una alerta, no todos los días

---

## 7. Publicación y compartir

1. Clic en **"Compartir"** → **"Obtener enlace"** → Cualquier usuario con el enlace puede ver
2. Para el portafolio: copiar el enlace público al README del repositorio
3. Nombre del informe: `Retail Postventa Analytics 2024 — Julio Prad`
