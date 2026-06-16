# Retail Postventa Analytics — Plan del Proyecto

## 1. Resumen ejecutivo

Proyecto de portafolio de Data Analyst que modela end-to-end la analítica
de postventa de un retailer e-commerce LATAM. Integra órdenes, despachos,
contactos y devoluciones en un solo modelo dimensional en BigQuery,
construye marts de KPIs operacionales en dbt, y los visualiza en
**Looker Studio y Power BI** (mismo modelo, dos herramientas).

Construido con estándares de **ingeniería de software profesional**:
gestión de dependencias con uv, linting con Ruff, tipos estáticos con
mypy, hooks de pre-commit y CI/CD en GitHub Actions.

**Pregunta de negocio:**
> ¿Cuántos contactos genera cada orden de e-commerce, por qué motivos,
> y cómo podemos predecir y reducir los contactos evitables?

**Inspiración del dominio:** operaciones omnicanales tipo Lider.cl /
Walmart Chile. Datos 100% sintéticos generados con Python; ningún dato
real de empresas.

---

## 2. Estado por módulo

| Módulo | Nombre | Estado |
|---|---|---|
| 0 | Setup base + tooling de calidad | 🚧 Por iniciar |
| 1 | Generadores de datos sintéticos | 🚧 Por iniciar |
| 2 | Carga a BigQuery raw | 🚧 Por iniciar |
| 3 | dbt staging | 🚧 Por iniciar |
| 4 | dbt dimensional (dim + fct) | 🚧 Por iniciar |
| 5 | dbt marts (KPIs) | 🚧 Por iniciar |
| 6 | Dashboards Looker + Power BI | 🚧 Por iniciar |
| 7 | Modelo predictivo (regresión logística) | 🚧 Expansión post-MVP |
| 8 | Orquestación con Airflow local | 🚧 Expansión post-MVP |

**Regla:** los módulos 7 y 8 son expansiones opcionales. El MVP entregable
son los módulos 0-6. No iniciar 7 ni 8 antes de cerrar 0-6.

---

## 3. Stack técnico

### 3.1 Capas funcionales

| Capa | Tecnología | Decisión |
|---|---|---|
| Lenguaje | Python 3.11+ | Generadores + scripts |
| Gestor de paquetes | **uv** | Único gestor; jamás `pip` ni `venv` manual |
| Storage | BigQuery (Sandbox o real) | Sin requerimiento de tarjeta |
| Transformación | **dbt-bigquery** | Reemplaza SQL suelto |
| Visualización | **Looker Studio + Power BI** | Mismo modelo, dos herramientas |
| Orquestación (M8) | **Airflow local (standalone)** | Sin costo, diseñado para Cloud Composer |
| ML (M7) | scikit-learn | Regresión logística |

### 3.2 Tooling de calidad de código (obligatorio)

| Herramienta | Rol | Cómo se ejecuta |
|---|---|---|
| **Ruff** | Linter + formatter (reemplaza Black, Flake8, isort) | `ruff check .` / `ruff format .` |
| **mypy** | Type checker estático | `mypy .` |
| **pytest** | Framework de tests unitarios | `pytest` |
| **pre-commit** | Hook que corre Ruff + mypy antes de cada commit | Auto-activado |
| **GitHub Actions** | CI/CD en cada push y PR | `.github/workflows/ci.yml` |
| **uv** | Comando único para todo: `uv run`, `uv add`, `uv sync` | NUNCA `pip` |

**Regla crítica:** ningún commit puede ingresar al repo si no pasa
pre-commit. Ningún PR puede mergearse si CI está rojo.

---

## 4. Arquitectura

```
Generadores Python (data_gen/*.py)
    ↓
CSVs en data_gen/csv/
    ↓
BigQuery raw (5 tablas: orders, shipments, contacts, returns, surveys)
    ↓
dbt staging (limpieza, normalización, documentación de supuestos)
    ↓
dbt dimensional (star schema: 7 dim + 4 fct)
    ↓
dbt marts (7 marts de KPIs + 1 mart de alertas)
    ↓
┌────────────────────┬────────────────────┐
Looker Studio        Power BI Desktop
(dashboard 3 págs)   (dashboard 2 págs)
```

**Principio rector:** la lógica de negocio (definición de KPIs, cálculos)
vive en SQL en BigQuery vía dbt, NO en la herramienta de BI. Looker y
Power BI son consumidores; el warehouse es la fuente única de verdad.

---

## 5. Modelo de datos sintéticos

### 5.1 Las 5 fuentes (CSVs generados)

| Archivo | Filas estimadas | Descripción |
|---|---|---|
| `orders.csv` | ~10.000 | Órdenes del último año (cliente, fecha, monto, productos, región) |
| `shipments.csv` | ~10.000 | Un despacho por orden (carrier, fecha prometida vs real, estado) |
| `contacts.csv` | ~3.500 | Contactos postventa (~35% de las órdenes generan al menos uno) |
| `returns.csv` | ~1.200 | Devoluciones (~12% de las órdenes) |
| `surveys.csv` | ~2.000 | Encuestas post-contacto (~60% de los contactos atendidos) |

### 5.2 Reglas de coherencia (CRÍTICAS)

- Cada `contact` referencia una `order` existente.
- La fecha de un contacto es **posterior** al despacho asociado.
- Si un envío se atrasó (delivery_date > promised_date), aumenta la
  probabilidad de contacto subsecuente.
- Una `return` solo existe si hubo `order` + `shipment` previos.
- `surveys` solo para contactos NO abandonados.
- Contactos abandonados no tienen `agente_id`, `aht`, `csat`, `fcr`.

Estas reglas son lo que hace que el análisis sea creíble. Sin ellas,
los KPIs en BigQuery mienten.

---

## 6. Modelo dimensional (star schema)

### 6.1 Dimensiones

| Tabla | Atributos clave |
|---|---|
| `dim_date` | Calendario completo 2024-2026 |
| `dim_customer` | id, segmento (nuevo / recurrente / VIP), región, ciudad |
| `dim_product` | sku, categoría, sub-categoría, precio promedio |
| `dim_region` | región, zona logística (metro / regiones) |
| `dim_carrier` | nombre, modalidad (express / normal) |
| `dim_channel` | canal de contacto (voz, chat, app, correo) |
| `dim_motivo` | catálogo de motivos (despacho, postventa, reclamo, pagos, info) |

### 6.2 Hechos

| Tabla | Granularidad |
|---|---|
| `fct_orders` | 1 fila = 1 orden |
| `fct_shipments` | 1 fila = 1 despacho |
| `fct_contacts` | 1 fila = 1 contacto (tabla "estrella" del proyecto) |
| `fct_returns` | 1 fila = 1 devolución |

---

## 7. Marts (los KPIs accionables)

| Mart | Pregunta de negocio que responde |
|---|---|
| `mart_cpo_semanal` | ¿Cuántos contactos por orden tenemos por semana? |
| `mart_cpo_por_motivo` | ¿Qué motivos concentran los contactos? |
| `mart_otd_vs_sla` | ¿Estamos cumpliendo la promesa de entrega? |
| `mart_correlacion_otd_cpo` | ⭐ ¿Cuánto sube CPO cuando OTD baja? *(insight estrella)* |
| `mart_devoluciones_motivo` | ¿Cuáles devoluciones podríamos prevenir? |
| `mart_kpis_contact_center` | SLA, AHT, FCR, abandono, CSAT |
| `mart_alerts_diarias` | ¿Qué se salió del rango hoy? (P1/P2 con owner) |

### 7.1 El insight estrella

Aterrizado como una hipótesis testeable:

> *Cuando el OTD (On-Time Delivery) cae bajo el 90%, el CPO (Contacts Per
> Order) sube de ~0.3 a ~0.7. Un cliente con envío atrasado genera el
> doble de contactos. **Prevenir un retraso es prevenir dos contactos.***

Este insight es la conclusión central del proyecto y debe ser visible
en el README, en el dashboard ejecutivo, y en `docs/insights.md`.

---

## 8. Dashboards

### 8.1 Looker Studio — Operacional (3 páginas)

| Página | Contenido |
|---|---|
| Executive Overview | Scorecards: CPO global, OTD%, devoluciones, contactos totales |
| Operación Diaria | CPO por semana, motivos top, contactos por canal, mapa regional |
| Predictor & Alertas | Top 50 órdenes con mayor riesgo (M7), alertas P1/P2 activas |

URL pública + screenshots en `dashboards/looker/`.

### 8.2 Power BI Desktop — Ejecutivo (2 páginas)

| Página | Contenido |
|---|---|
| Strategic View | KPIs hero + tendencia mensual + correlación OTD↔CPO |
| Drill-through Detail | Drill desde KPI a nivel orden/cliente/contacto |

Archivo `.pbix` en `dashboards/powerbi/` + screenshots.

### 8.3 Principio compartido

**Cero lógica de KPI vive en la herramienta de BI.** Los dashboards solo
leen tablas finales de BigQuery (`mart_*`). Si un KPI necesita cambiar,
se cambia en dbt; ambos dashboards reflejan automáticamente.

---

## 9. Módulo 0 — Setup base + tooling de calidad

**Este módulo se completa antes de cualquier otra cosa.** Define las
reglas operacionales del repo.

### 9.1 Entregables

- `pyproject.toml` con dependencias declaradas (gestionadas por uv).
- `uv.lock` versionado para reproducibilidad exacta.
- Configuración de **Ruff** (en `pyproject.toml`, sección `[tool.ruff]`).
- Configuración de **mypy** (en `pyproject.toml`, sección `[tool.mypy]`).
- `.pre-commit-config.yaml` con hooks Ruff + mypy.
- `.github/workflows/ci.yml` con jobs: lint, type-check, test.
- Badge de CI verde visible en el README.
- `.gitignore` (incluye `.venv/`, `dbt_packages/`, `profiles.yml`).

### 9.2 Configuración mínima de Ruff

```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "F",    # pyflakes
    "I",    # isort
    "B",    # flake8-bugbear
    "UP",   # pyupgrade
    "N",    # pep8-naming
    "C90",  # mccabe complexity
]
```

### 9.3 Configuración mínima de mypy

```toml
[tool.mypy]
python_version = "3.11"
strict = true
ignore_missing_imports = true
warn_unused_ignores = true
```

### 9.4 GitHub Actions — workflow mínimo

`.github/workflows/ci.yml` debe ejecutar en cada push y PR:

1. Checkout del repo.
2. Setup de Python 3.11+.
3. Instalación de uv.
4. `uv sync` para crear el entorno.
5. `uv run ruff check .`
6. `uv run ruff format --check .`
7. `uv run mypy .`
8. `uv run pytest` (si hay tests).

Si cualquier paso falla, el check de GitHub queda rojo y el badge del
README se actualiza automáticamente.

---

## 10. Módulos 7 y 8 (expansiones post-MVP)

### 10.1 Módulo 7 — Modelo predictivo

**Objetivo:** dado lo que sabemos de una orden al momento de crearse,
estimar la probabilidad de que genere contacto postventa.

- Algoritmo: regresión logística (scikit-learn).
- Features: segmento cliente, categoría producto, modalidad despacho,
  histórico carrier-región, histórico de contacto del cliente.
- Output: una columna `prob_contacto` en una tabla BigQuery, refrescada
  diariamente, alimentando el dashboard.
- Métricas: precision, recall, AUC. Documentadas en
  `docs/predictor_methodology.md`.
- Tests unitarios en `tests/test_predictor.py`.

### 10.2 Módulo 8 — Orquestación Airflow

**Objetivo:** ejecutar todo el pipeline diariamente sin intervención.

DAG: `dag_retail_postventa.py`

```
1. cargar_csvs_a_bq            (PythonOperator)
2. dbt_run_staging             (BashOperator: dbt run --select staging)
3. dbt_test_staging            (dbt test sobre staging)
4. dbt_run_dimensional         (dbt run --select marts.dim marts.fct)
5. dbt_run_marts               (dbt run --select marts.mart_*)
6. entrenar_predictor (M7)     (PythonOperator)
7. notificar_completado        (placeholder Slack/email)
```

- Reintentos: 3 por tarea.
- Si una tarea falla las 3 veces, alerta.
- Documentado como "diseñado para Cloud Composer, ejecutado localmente
  con Airflow standalone para portafolio sin costo".

---

## 11. Estructura del repositorio

```
retail-postventa-analytics/
├── README.md
├── CLAUDE.md
├── PROJECT_PLAN.md           ← este archivo
├── pyproject.toml            ← uv, ruff, mypy en un solo archivo
├── uv.lock
├── .gitignore
├── .pre-commit-config.yaml
├── .github/
│   └── workflows/
│       └── ci.yml            ← GitHub Actions: lint + type + test
├── data_gen/
│   ├── generar_orders.py
│   ├── generar_shipments.py
│   ├── generar_contacts.py
│   ├── generar_returns.py
│   ├── generar_surveys.py
│   └── csv/                  ← outputs generados (gitignored)
├── config/
│   └── settings.py           ← catálogos, parámetros, IDs
├── scripts/
│   ├── upload_to_bq.py
│   └── crear_dataset_bq.py
├── dbt_project/
│   ├── dbt_project.yml
│   ├── profiles.yml          (en .gitignore: contiene credenciales)
│   ├── models/
│   │   ├── staging/
│   │   ├── dimensional/
│   │   └── marts/
│   └── tests/
├── ml/                       ← Módulo 7
│   ├── train_predictor.ipynb
│   ├── train_predictor.py
│   └── model_artifacts/
├── orchestration/            ← Módulo 8
│   └── dag_retail_postventa.py
├── tests/                    ← tests unitarios pytest
│   ├── test_generadores.py
│   ├── test_settings.py
│   └── test_predictor.py
├── dashboards/
│   ├── looker/
│   │   ├── url.md
│   │   └── screenshots/
│   └── powerbi/
│       ├── retail_postventa.pbix
│       └── screenshots/
└── docs/
    ├── pregunta_negocio.md
    ├── data_model.md
    ├── star_schema.md
    ├── kpi_definitions.md
    ├── insights.md           ← documento estrella
    ├── predictor_methodology.md  (M7)
    └── airflow_dag.md            (M8)
```

---

## 12. Variables de entorno requeridas

```bash
export GCP_PROJECT_ID=<tu-proyecto-bq>
export GCP_BQ_DATASET=retail_postventa
export PYTHONPATH=.
```

Credenciales GCP: cuenta de servicio JSON en variable
`GOOGLE_APPLICATION_CREDENTIALS`, o autenticación con
`gcloud auth application-default login`.

---

## 13. Convenciones de código

### 13.1 Estilo (impuesto por Ruff)

- Python 3.11+, type hints obligatorios en funciones públicas.
- Line length: 100 caracteres.
- Imports agrupados automáticamente por Ruff (stdlib → externas → proyecto).
- f-strings, no `.format()` ni `%`.
- Docstrings al estilo Google (`Args:`, `Returns:`).

### 13.2 Tipos (impuesto por mypy en modo strict)

- Toda función pública debe tener type hints en argumentos y retorno.
- No `Any` salvo justificación documentada.
- `None` debe declararse explícitamente cuando una función no retorna.

### 13.3 Tests (pytest)

- Cada módulo de Python con lógica no trivial debe tener tests.
- Cobertura mínima recomendada: 70% para módulos de generadores y ML.
- Tests rápidos: ningún test debe demorar más de 1 segundo.

### 13.4 Configuración

- Catálogos del negocio SOLO en `config/settings.py`.
- IDs cloud por variables de entorno, nunca hardcodeados.
- Scripts idempotentes (catch `AlreadyExists` en setup).

### 13.5 dbt

- Nombres `snake_case`.
- Staging con prefijo `stg_`, dimensionales con `dim_` / `fct_`,
  marts con `mart_`.
- Cada modelo dbt debe tener al menos un test (`unique`, `not_null`,
  `relationships`).

### 13.6 Commits y branches

- Conventional Commits: `feat:`, `fix:`, `docs:`, `refactor:`, `chore:`,
  `test:`, `ci:`.
- Branch principal: `main`.
- Para cambios significativos: branches `feat/nombre-feature` con PR.

### 13.7 Gestión de dependencias

- **NUNCA** `pip install`. Siempre `uv add <paquete>`.
- **NUNCA** editar `pyproject.toml` a mano para deps; usar `uv add`.
- `uv.lock` SÍ se versiona (reproducibilidad).
- Para correr scripts: `uv run python <script>.py`.
- Para tests: `uv run pytest`.
- Para linting: `uv run ruff check .`.

---

## 14. Smoke test de cierre del MVP

Al finalizar Módulo 6, este flujo debe correr sin intervención:

```bash
# 0. Verificar calidad de código
uv run ruff check .
uv run ruff format --check .
uv run mypy .
uv run pytest

# 1. Generar datos sintéticos
uv run python data_gen/generar_orders.py
uv run python data_gen/generar_shipments.py
uv run python data_gen/generar_contacts.py
uv run python data_gen/generar_returns.py
uv run python data_gen/generar_surveys.py

# 2. Cargar a BigQuery
uv run python scripts/upload_to_bq.py

# 3. Correr dbt completo
cd dbt_project && dbt run && dbt test

# 4. Validar marts
bq query --use_legacy_sql=false "SELECT * FROM ${GCP_BQ_DATASET}.mart_correlacion_otd_cpo LIMIT 10"

# 5. Refrescar dashboards (manual: ambos consumen las marts en BQ)
```

Si los 5 pasos completan sin error y el CI de GitHub está verde, el MVP
está cerrado.

---

## 15. Lo que este proyecto demuestra (para entrevistas)

| Capacidad | Evidencia |
|---|---|
| Modelado dimensional | Star schema con 7 dim + 4 fct |
| SQL analítico avanzado | Window functions, CTEs, correlaciones |
| **dbt** | Pipeline transformación con tests, docs auto-generadas |
| Integración multi-fuente | 5 fuentes consolidadas en un modelo coherente |
| KPIs de dominio retail | CPO, OTD, devoluciones, SLA contact center |
| **Dos herramientas BI** | Looker Studio + Power BI sobre el mismo warehouse |
| Estadística aplicada (M7) | Regresión logística con métricas de evaluación |
| Orquestación (M8) | DAG Airflow con reintentos y alertas |
| **Calidad de software** | Ruff + mypy + pytest + pre-commit + GitHub Actions |
| Documentación profesional | Assumptions, KPI definitions, insights, runbook |

---

## 16. Conexión con los otros proyectos del portafolio

| Proyecto | Aporta a este |
|---|---|
| `latam-uniforms-portfolio` | Patrón de staging → dimensional → marts |
| `staff-sizing-portfolio` | Patrón de forecast y dotación |
| `torre-control-contact-center` | Modelo de eventos de contact center (M1) |

**Narrativa para la entrevista:**

> *"Mi portafolio cubre operación retail desde cuatro ángulos:
> planificación de recursos (uniforms), modelado de demanda (staff-sizing),
> monitoreo en tiempo real (torre-control), y analítica integral de
> postventa (retail-postventa). Este último integra las tres dimensiones
> en un solo modelo y un solo dashboard, con estándares de ingeniería de
> software profesional —CI/CD, linting, tipos estáticos—. Es lo más
> parecido al trabajo real que entiendo se hace en torre de control retail."*
