# Power BI — Especificación Completa del Dashboard
## Retail Postventa Analytics 2024

**Proyecto GCP:** `project-5089395c-793b-4923-a0d`
**Dataset marts:** `retail_postventa_marts`

> **Nota de plataforma:** Power BI Desktop requiere Windows.
> En macOS, usar **Power BI Service** (app.powerbi.com) con el conector BigQuery,
> o Power BI Desktop dentro de una VM con Windows (Parallels, UTM, etc.).
> Las instrucciones de conexión aplican a ambos.

---

## 1. Configuración inicial

### 1.1 Conectar a BigQuery

**En Power BI Desktop (Windows):**
1. Inicio → **Obtener datos → Google BigQuery**
2. Autenticar con `prad3nas@gmail.com` → cuenta organizacional OAuth
3. Seleccionar proyecto `project-5089395c-793b-4923-a0d`

**En Power BI Service (web, macOS):**
1. app.powerbi.com → **Nuevo → Informe**
2. Seleccionar una fuente de datos → **Google BigQuery**
3. Autenticar con OAuth

### 1.2 Importar las 7 tablas

En el navegador de datos, expandir:
`project-5089395c-793b-4923-a0d → retail_postventa_marts`

Marcar las 7 tablas y hacer clic en **Cargar** (no en Transformar todavía):

```
mart_cpo_semanal
mart_cpo_por_motivo
mart_otd_vs_sla
mart_correlacion_otd_cpo
mart_kpis_contact_center
mart_alerts_diarias
mart_devoluciones_motivo
```

### 1.3 Modelo de datos (vista Modelo)

Las tablas son marts independientes (no tienen relaciones entre sí en el modelo).
No crear relaciones. Cada visual usa una sola tabla fuente.

### 1.4 Medidas DAX a crear

Ir a **Vista de tabla → seleccionar tabla → Nueva medida** para cada una:

**En `mart_cpo_semanal`:**

```dax
CPO Promedio =
AVERAGE(mart_cpo_semanal[cpo])

Total Contactos =
SUM(mart_cpo_semanal[n_contacts])

Total Ordenes =
SUM(mart_cpo_semanal[n_orders])
```

**En `mart_otd_vs_sla`:**

```dax
OTD Global =
DIVIDE(
    SUM(mart_otd_vs_sla[n_on_time]),
    SUM(mart_otd_vs_sla[n_shipments])
)

Total Atrasados =
SUM(mart_otd_vs_sla[n_late])

Tasa Atraso =
DIVIDE(
    SUM(mart_otd_vs_sla[n_late]),
    SUM(mart_otd_vs_sla[n_shipments])
)
```

**En `mart_kpis_contact_center`:**

```dax
AHT Minutos Prom =
AVERAGEX(
    mart_kpis_contact_center,
    mart_kpis_contact_center[avg_aht_seconds] / 60
)

FCR Pct Prom =
AVERAGE(mart_kpis_contact_center[fcr_rate])

Abandon Pct Prom =
AVERAGE(mart_kpis_contact_center[abandon_rate])

CSAT Prom =
AVERAGE(mart_kpis_contact_center[avg_csat])
```

**En `mart_correlacion_otd_cpo`:**

```dax
CPO Prompt OTD Alto =
CALCULATE(
    AVERAGE(mart_correlacion_otd_cpo[cpo]),
    mart_correlacion_otd_cpo[otd_bucket] = "OTD >= 90%"
)

CPO Cuando OTD Bajo =
CALCULATE(
    AVERAGE(mart_correlacion_otd_cpo[cpo]),
    mart_correlacion_otd_cpo[otd_bucket] <> "OTD >= 90%"
)
```

**En `mart_alerts_diarias`:**

```dax
Dias P1 =
COUNTROWS(
    FILTER(
        mart_alerts_diarias,
        mart_alerts_diarias[otd_alert] = "P1" ||
        mart_alerts_diarias[abandon_alert] = "P1" ||
        mart_alerts_diarias[csat_alert] = "P1"
    )
)

Dias P2 =
COUNTROWS(
    FILTER(
        mart_alerts_diarias,
        mart_alerts_diarias[otd_alert] = "P2" ||
        mart_alerts_diarias[abandon_alert] = "P2" ||
        mart_alerts_diarias[csat_alert] = "P2"
    )
)
```

**En `mart_devoluciones_motivo`:**

```dax
Total Devoluciones =
SUM(mart_devoluciones_motivo[n_returns])

Pct Late Related =
DIVIDE(
    SUM(mart_devoluciones_motivo[n_late_related]),
    SUM(mart_devoluciones_motivo[n_returns])
)
```

### 1.5 Formato de columnas (Vista de tabla)

En `mart_cpo_semanal`:
- `week_start` → Tipo: Fecha → Formato: "dd/MM/yyyy"
- `cpo` → Tipo: Número decimal → Formato: 3 decimales

En `mart_otd_vs_sla`:
- `otd_rate` → Tipo: Número decimal → Formato: porcentaje 1 decimal

En `mart_kpis_contact_center`:
- `week_start` → Tipo: Fecha
- `fcr_rate`, `abandon_rate` → Formato: porcentaje 1 decimal
- `avg_csat` → Formato: número 2 decimales

---

## 2. Paleta de colores y tema

### 2.1 Importar tema personalizado

**Vista → Temas → Buscar temas → Importar tema** → crear archivo `tema.json`:

```json
{
  "name": "Retail Postventa",
  "dataColors": [
    "#1A73E8",
    "#34A853",
    "#EA4335",
    "#FBBC04",
    "#46BDC6",
    "#7B61FF"
  ],
  "background": "#FFFFFF",
  "foreground": "#202124",
  "tableAccent": "#1A73E8",
  "visualStyles": {
    "*": {
      "*": {
        "fontFamily": [{"value": "Segoe UI"}]
      }
    }
  }
}
```

Guardar como `dashboards/powerbi/tema.json` e importarlo.

### 2.2 Colores de referencia

| Significado | Hex |
|---|---|
| Principal (azul) | `#1A73E8` |
| OK / verde | `#34A853` |
| Alerta P1 / rojo | `#EA4335` |
| Alerta P2 / amarillo | `#FBBC04` |
| Neutro gris | `#9AA0A6` |
| Fondo gris claro | `#F8F9FA` |

---

## 3. Página 1: Resumen Ejecutivo

**Nombre de página:** `Resumen Ejecutivo`

### 3.1 Encabezado

- Visual: **Cuadro de texto**
- Texto: `Retail Postventa Analytics — Resumen 2024`
- Fondo: `#1A73E8`, texto blanco, 20px negrita
- Tamaño: ancho completo × 50px

### 3.2 Segmentador de fechas

- Visual: **Segmentación de datos** (tipo: entre)
- Tabla: `mart_cpo_semanal`
- Campo: `week_start`
- Formato: rango de fechas con selector de calendario
- Valor inicial: 01/01/2024 – 31/12/2024

### 3.3 Tarjetas KPI (fila de 4)

**Tarjeta 1 — CPO**
- Visual: **Tarjeta**
- Valor: medida `CPO Promedio` (tabla `mart_cpo_semanal`)
- Etiqueta: `CPO Promedio`
- Formato: 3 decimales

**Tarjeta 2 — OTD**
- Visual: **Tarjeta**
- Valor: medida `OTD Global`
- Etiqueta: `OTD Global`
- Formato: porcentaje 1 decimal

**Tarjeta 3 — Contactos**
- Visual: **Tarjeta**
- Valor: medida `Total Contactos`
- Etiqueta: `Total Contactos 2024`
- Formato: entero separado por miles

**Tarjeta 4 — Órdenes**
- Visual: **Tarjeta**
- Valor: medida `Total Ordenes`
- Etiqueta: `Total Órdenes 2024`
- Formato: entero separado por miles

### 3.4 Gráfico de línea: Evolución CPO semanal

- Visual: **Gráfico de líneas**
- Eje X: `mart_cpo_semanal[week_start]` (nivel: semana)
- Valores Y: `mart_cpo_semanal[cpo]` → nombre "CPO"
- Línea constante: valor = 0.35, nombre "Target", color rojo discontinua
  *(Agregar en: Formato → Líneas de referencia → Agregar línea)*
- Leyenda: activada
- Título: `CPO Semanal 2024`
- Marcadores: activados

### 3.5 Gráfico de barras agrupadas: OTD por carrier × zona

- Visual: **Gráfico de barras agrupadas**
- Eje Y (categorías): `mart_otd_vs_sla[carrier]`
- Eje X (valores): `mart_otd_vs_sla[otd_rate]`
- Leyenda: `mart_otd_vs_sla[zone]`
- Ordenar: `otd_rate` ascendente
- Formato del eje X: porcentaje
- Línea de referencia: 0.90 (color rojo)
- Título: `OTD por Carrier y Zona`

---

## 4. Página 2: Impacto del Atraso ⭐

**Nombre de página:** `Impacto del Atraso`

### 4.1 Banner

- Visual: **Cuadro de texto** (fondo `#34A853`)
- Texto: `⭐ Las órdenes atrasadas generan contacto 2.4× más que las entregadas en tiempo`
- Color texto: blanco, 16px negrita

### 4.2 Tarjetas comparativas

**Tarjeta — CPO con OTD alto**
- Valor: medida `CPO Prompt OTD Alto`
- Etiqueta: `CPO — OTD ≥ 90%`
- Fondo de la tarjeta: `#34A853` claro
- Formato: 3 decimales

**Tarjeta — CPO con OTD bajo**
- Valor: medida `CPO Cuando OTD Bajo`
- Etiqueta: `CPO — OTD < 90%`
- Fondo de la tarjeta: `#EA4335` claro
- Formato: 3 decimales

**Tarjeta — Tasa de atraso**
- Valor: medida `Tasa Atraso`
- Etiqueta: `% Órdenes con Atraso`
- Formato: porcentaje 1 decimal

### 4.3 Gráfico de dispersión: OTD vs CPO por semana

- Visual: **Gráfico de dispersión**
- Valores X: `mart_correlacion_otd_cpo[otd_rate]`
- Valores Y: `mart_correlacion_otd_cpo[cpo]`
- Tamaño: `mart_correlacion_otd_cpo[n_orders]`
- Leyenda: `mart_correlacion_otd_cpo[otd_bucket]`
  - `OTD >= 90%` → `#34A853`
  - `OTD 80-90%` → `#FBBC04`
  - `OTD < 80%` → `#EA4335`
- Detalles: `mart_correlacion_otd_cpo[week_start]` (tooltip)
- Título del eje X: `OTD Rate`
- Título del eje Y: `CPO`
- Título: `OTD vs CPO por Semana`

### 4.4 Gráfico de barras: Motivos de contacto

- Visual: **Gráfico de barras horizontales**
- Eje Y (categorías): `mart_cpo_por_motivo[contact_motivo]`
- Eje X (valores): `mart_cpo_por_motivo[n_contacts]`
- Información sobre herramientas: `mart_cpo_por_motivo[pct_of_contacts]`
- Ordenar: `n_contacts` descendente
- Etiquetas de datos: activadas (formato entero)
- Título: `Motivos de Contacto Postventa`

---

## 5. Página 3: Contact Center

**Nombre de página:** `Contact Center`

### 5.1 Segmentador de semanas

- Visual: **Segmentación de datos**
- Tabla: `mart_kpis_contact_center`
- Campo: `week_start`
- Tipo: entre (rango de fechas)

### 5.2 Tarjetas KPI (fila de 4)

| Tarjeta | Medida | Formato | Referencia |
|---|---|---|---|
| FCR Rate | `FCR Pct Prom` | % 1 dec. | Target ≥ 68% |
| Abandon Rate | `Abandon Pct Prom` | % 1 dec. | Target < 15% |
| AHT Promedio | `AHT Minutos Prom` | nro 1 dec. + " min" | — |
| CSAT Promedio | `CSAT Prom` | nro 2 dec. | Target ≥ 3.5 |

### 5.3 Gráfico de líneas: FCR y Abandon semanales

- Visual: **Gráfico de líneas**
- Eje X: `mart_kpis_contact_center[week_start]`
- Línea 1: `mart_kpis_contact_center[fcr_rate]` → nombre "FCR", color `#34A853`
- Línea 2: `mart_kpis_contact_center[abandon_rate]` → nombre "Abandon", color `#EA4335`
- Eje Y secundario: no (mismo eje, ambas en formato porcentaje)
- Título: `FCR vs Abandon Rate Semanal`

### 5.4 Gráfico de columnas: Contactos semanales con detalle abandono

- Visual: **Gráfico de columnas apiladas**
- Eje X: `mart_kpis_contact_center[week_start]`
- Valores:
  - `mart_kpis_contact_center[n_abandoned]` → "Abandonados", color `#EA4335`
  - calculado = `n_contacts_total - n_abandoned` → "Atendidos", color `#1A73E8`
  *(crear medida: `Contactos Atendidos = SUM(mart_kpis_contact_center[n_contacts_total]) - SUM(mart_kpis_contact_center[n_abandoned])`)*
- Título: `Volumen de Contactos Semanal`

### 5.5 Gráfico de línea: CSAT semanal

- Visual: **Gráfico de líneas con área sombreada**
- Eje X: `mart_kpis_contact_center[week_start]`
- Valores Y: `mart_kpis_contact_center[avg_csat]`
- Línea de referencia: 3.5
- Eje Y: mínimo 1, máximo 5
- Título: `CSAT Promedio Semanal`

### 5.6 Tabla detalle

- Visual: **Tabla**
- Columnas:
  - `week_start` (formato dd/MM)
  - `n_contacts_total`
  - `abandon_rate` (%)
  - `avg_aht_seconds` (seg)
  - `fcr_rate` (%)
  - `avg_csat`
- Ordenar: `week_start` desc
- Formato condicional en `abandon_rate`: escala rojo (> 20%) a verde (< 10%)

---

## 6. Página 4: Devoluciones

**Nombre de página:** `Devoluciones`

### 6.1 Tarjetas resumen

**Tarjeta — Total devoluciones**
- Medida: `Total Devoluciones`
- Etiqueta: `Total Devoluciones 2024`

**Tarjeta — Tasa de devolución**
- Medida: `DIVIDE([Total Devoluciones], 10000)`
- Etiqueta: `Tasa de Devolución`
- Formato: porcentaje 1 decimal

**Tarjeta — % relacionadas con atraso**
- Medida: `Pct Late Related`
- Etiqueta: `% Relacionadas con Atraso`
- Formato: porcentaje 1 decimal

### 6.2 Gráfico de anillo: Devoluciones por motivo

- Visual: **Gráfico de anillos**
- Leyenda: `mart_devoluciones_motivo[return_motivo]`
- Valores: `mart_devoluciones_motivo[n_returns]`
- Etiquetas de detalle: activadas (nombre + porcentaje)
- Título: `Distribución por Motivo`

### 6.3 Gráfico de barras: Relación con atraso por motivo

- Visual: **Gráfico de barras apiladas 100%**
- Eje Y: `mart_devoluciones_motivo[return_motivo]`
- Segmento 1: `mart_devoluciones_motivo[n_late_related]`
  - Nombre: "Relacionada con atraso", color `#EA4335`
- Segmento 2: medida `n_returns - n_late_related`
  - Nombre: "Sin relación con atraso", color `#9AA0A6`
- Etiqueta de datos: porcentaje
- Título: `% Relación con Atraso por Motivo`

### 6.4 Tabla de detalle

- Visual: **Tabla**
- Columnas: `return_motivo`, `n_returns`, `pct_of_returns`, `n_late_related`, `pct_late_related`
- Formato condicional en `pct_late_related`: escala de color
  - Mínimo: blanco, Máximo: `#EA4335`
- Ordenar: `n_returns` desc

---

## 7. Página 5: Alertas Operativas

**Nombre de página:** `Alertas`

### 7.1 Tarjetas de resumen de alertas

**Tarjeta — Días P1** (fondo rojo si > 0)
- Medida: `Dias P1`
- Etiqueta: `Días con Alerta P1`
- Formato condicional de fondo: si valor > 0 → fondo `#EA4335`, texto blanco

**Tarjeta — Días P2** (fondo amarillo si > 0)
- Medida: `Dias P2`
- Etiqueta: `Días con Alerta P2`

### 7.2 Tabla de alertas (principal)

- Visual: **Tabla**
- Columnas y fuente (`mart_alerts_diarias`):

| Columna mostrada | Campo | Formato |
|---|---|---|
| Fecha | `metric_date` | dd/MM/yyyy |
| OTD | `otd_rate` | % 1 dec. |
| Alerta OTD | `otd_alert` | texto |
| Owner | `otd_owner` | texto |
| Abandon | `abandon_rate` | % 1 dec. |
| Alerta Abandono | `abandon_alert` | texto |
| CSAT | `avg_csat` | número 2 dec. |
| Alerta CSAT | `csat_alert` | texto |

- Formato condicional en columnas `*_alert`:
  - Valor = "P1" → fondo `#EA4335`, texto blanco
  - Valor = "P2" → fondo `#FBBC04`
  - *(En Power BI: Formato de columna → Formato condicional → Color de fondo → Reglas)*

- Ordenar: `metric_date` descendente

### 7.3 Gráfico de línea: OTD diario

- Visual: **Gráfico de líneas**
- Eje X: `mart_alerts_diarias[metric_date]`
- Valores Y: `mart_alerts_diarias[otd_rate]`
- Color línea: `#1A73E8`
- Líneas de referencia:
  - 0.90 → nombre "Umbral P2", color amarillo, discontinua
  - 0.80 → nombre "Umbral P1", color rojo, discontinua
- Área sombreada: activada
- Título: `OTD en Días con Alertas Activas`

---

## 8. Opciones de publicación

### Power BI Service

1. En Power BI Desktop: **Publicar → Mi área de trabajo**
2. En app.powerbi.com: el informe aparece en "Mi área de trabajo"
3. Compartir: **Compartir → Copiar vínculo** → cualquier persona con el enlace

### Exportar a PDF (para portafolio)

- **Archivo → Exportar → Exportar a PDF**
- Incluir todas las páginas
- Guardar en `dashboards/powerbi/retail_postventa_dashboard.pdf`

### Archivo .pbix

- Guardar como `dashboards/powerbi/retail_postventa.pbix`
- Agregar al `.gitignore` si contiene credenciales embebidas
- O limpiar credenciales y versionar (el archivo .pbix es binario, pero git lo puede versionar)
