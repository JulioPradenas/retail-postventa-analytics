# Instrucciones para Claude Code — Retail Postventa Analytics

Este archivo guía a Claude Code para operar el proyecto.
**Leer antes de cualquier modificación.**

Para el plan completo del proyecto, ver `PROJECT_PLAN.md`.
Para contexto narrativo del dominio y motivación, ver `README.md`.

---

## 1. Resumen ejecutivo

Proyecto de portafolio de Data Analyst. Analítica end-to-end de postventa
e-commerce retail LATAM (inspirado en Lider.cl / Walmart Chile), datos
100% sintéticos. Stack: **BigQuery + dbt + Looker Studio + Power BI**,
con estándares de ingeniería de software profesional (uv, Ruff, mypy,
pre-commit, GitHub Actions).

**Pregunta de negocio:**
> ¿Cuántos contactos genera cada orden de e-commerce, por qué motivos,
> y cómo podemos predecir y reducir los contactos evitables?

---

## 2. Estado actual por módulo

| Módulo | Nombre | Estado |
|---|---|---|
| 0 | Setup base + tooling de calidad | ✅ Completo |
| 1 | Generadores de datos sintéticos | ✅ Completo |
| 2 | Carga a BigQuery raw | ✅ Completo |
| 3 | dbt staging | ✅ Completo |
| 4 | dbt dimensional (dim + fct) | ✅ Completo |
| 5 | dbt marts (KPIs) | ✅ Completo |
| 6 | Dashboards Looker + Power BI | ✅ Completo |
| 7 | Modelo predictivo (regresión logística) | ✅ Completo |
| 8 | Orquestación con Airflow local | ✅ Completo |

**Regla:** los módulos 🚧 NO se implementan sin confirmación explícita
del usuario. El plan en `PROJECT_PLAN.md` es referencia, no autorización.

**Regla adicional:** los módulos 7 y 8 son expansiones post-MVP y solo
se inician después de cerrar los módulos 0-6.

---

## 3. Stack obligatorio

### 3.1 Funcional

| Capa | Tecnología |
|---|---|
| Lenguaje | Python 3.11+ |
| Gestor de paquetes | **uv** (jamás pip ni venv manual) |
| Storage | BigQuery |
| Transformación | dbt-bigquery |
| Visualización | Looker Studio + Power BI |
| Orquestación (M8) | Airflow local standalone |
| ML (M7) | scikit-learn |

### 3.2 Calidad de código (obligatorio desde el Módulo 0)

| Herramienta | Comando |
|---|---|
| Ruff (lint + format) | `uv run ruff check .` / `uv run ruff format .` |
| mypy (types) | `uv run mypy .` |
| pytest (tests) | `uv run pytest` |
| pre-commit | Auto-activado en cada `git commit` |
| GitHub Actions | Auto en cada push/PR (`.github/workflows/ci.yml`) |

---

## 4. Reglas de oro para Claude Code

### 4.1 Gestión de dependencias

- **NUNCA** ejecutar `pip install`.
- **NUNCA** editar `pyproject.toml` a mano para agregar dependencias.
- **SIEMPRE** usar `uv add <paquete>` para nuevas dependencias.
- **SIEMPRE** usar `uv add --dev <paquete>` para dev dependencies
  (ruff, mypy, pytest, pre-commit).
- **SIEMPRE** ejecutar scripts con `uv run python <script>.py`.
- `uv.lock` se versiona (reproducibilidad exacta).

### 4.2 Calidad de código

- **NUNCA** hacer commit con código que no pase Ruff y mypy.
- **NUNCA** desactivar pre-commit hooks sin pedir autorización.
- **NUNCA** silenciar errores de mypy con `# type: ignore` sin un
  comentario explicando por qué.
- **SIEMPRE** agregar type hints en funciones públicas.
- **SIEMPRE** documentar funciones públicas con docstring estilo Google.

### 4.3 Configuración del proyecto

- Catálogos del negocio (canales, regiones, productos, motivos) viven
  SOLO en `config/settings.py`.
- Identificadores cloud (`GCP_PROJECT_ID`, `GCP_BQ_DATASET`) se leen
  de variables de entorno, nunca hardcodeados.
- Scripts de setup (crear dataset, cargar CSVs) deben ser **idempotentes**
  (capturar `AlreadyExists`).

### 4.4 Estilo de código (impuesto por Ruff)

- Python 3.11+, type hints obligatorios en funciones públicas.
- Line length: 100 caracteres.
- f-strings, no `.format()` ni `%`.
- Imports agrupados por Ruff automáticamente.
- Docstrings al estilo Google (`Args:`, `Returns:`, `Raises:`).

### 4.5 dbt

- Nombres `snake_case`.
- Prefijos: `stg_` (staging), `dim_` (dimensiones), `fct_` (hechos),
  `mart_` (marts de KPIs).
- Cada modelo dbt debe tener al menos un test (`unique`, `not_null`,
  `relationships` según corresponda).
- Documentar cada modelo en `schema.yml`.

### 4.6 Git y commits

- Conventional Commits obligatorios: `feat:`, `fix:`, `docs:`,
  `refactor:`, `chore:`, `test:`, `ci:`.
- Branch principal: `main`.
- Para cambios significativos: branch `feat/nombre-feature` con PR.
- **NUNCA** subir `.venv/`, `.env`, `profiles.yml`, credenciales JSON,
  o cualquier archivo listado en `.gitignore`.

### 4.7 Trabajo paso a paso

- **NO implementar varios módulos a la vez.** Un módulo cerrado y
  verificado antes de pasar al siguiente.
- **NO regenerar archivos completos** cuando se pide editar uno existente.
  Usar ediciones puntuales.
- **NO expandir el scope** sin pedir confirmación explícita.
- **SÍ pausar** después de cada paso significativo para que el usuario
  valide antes de avanzar.

---

## 5. Estructura del repositorio

```
retail-postventa-analytics/
├── README.md
├── CLAUDE.md                 ← este archivo
├── PROJECT_PLAN.md           ← plan completo del proyecto
├── pyproject.toml            ← uv + ruff + mypy en un archivo
├── uv.lock                   ← versionado
├── .gitignore
├── .pre-commit-config.yaml
├── .github/workflows/
│   └── ci.yml                ← lint + type + test
├── data_gen/                 ← Módulo 1
├── config/
│   └── settings.py
├── scripts/
├── dbt_project/              ← Módulos 3-5
├── ml/                       ← Módulo 7 (post-MVP)
├── orchestration/            ← Módulo 8 (post-MVP)
├── tests/                    ← pytest
├── dashboards/               ← Módulo 6
│   ├── looker/
│   └── powerbi/
└── docs/
```

---

## 6. Variables de entorno requeridas

Cada terminal nueva debe tener:

```bash
export GCP_PROJECT_ID=<tu-proyecto-bq>
export GCP_BQ_DATASET=retail_postventa
export PYTHONPATH=.
```

Autenticación GCP:
- Opción A: `gcloud auth application-default login`
- Opción B: `GOOGLE_APPLICATION_CREDENTIALS=/ruta/service-account.json`

---

## 7. Smoke test de validación

Después de cualquier cambio significativo, ejecutar:

```bash
# Calidad de código
uv run ruff check .
uv run ruff format --check .
uv run mypy .
uv run pytest

# Si hay cambios en dbt:
cd dbt_project && dbt run && dbt test
```

Resultado esperado: **todo pasa sin errores**. Si algo falla, NO seguir
adelante hasta resolverlo.

---

## 8. Modelo de datos (Módulo 1 — referencia)

### 8.1 Las 5 fuentes sintéticas

| Archivo | Filas | Descripción |
|---|---|---|
| `orders.csv` | ~10.000 | Órdenes (cliente, fecha, monto, productos, región) |
| `shipments.csv` | ~10.000 | Despachos (carrier, fecha prometida vs real, estado) |
| `contacts.csv` | ~3.500 | Contactos postventa (~35% de las órdenes) |
| `returns.csv` | ~1.200 | Devoluciones (~12% de las órdenes) |
| `surveys.csv` | ~2.000 | Encuestas post-contacto (~60% de los atendidos) |

### 8.2 Reglas de coherencia (CRÍTICAS)

- Cada `contact` referencia una `order` existente.
- Fecha de contacto **posterior** al despacho asociado.
- Envío atrasado → mayor probabilidad de contacto subsecuente.
- `return` solo si hubo `order` + `shipment`.
- `surveys` solo para contactos NO abandonados.
- Contactos abandonados: `agente_id`, `aht`, `csat`, `fcr` en `NULL`.

---

## 9. Marts a construir (Módulo 5 — referencia)

| Mart | Responde |
|---|---|
| `mart_cpo_semanal` | Contactos por orden por semana |
| `mart_cpo_por_motivo` | Motivos que concentran contactos |
| `mart_otd_vs_sla` | Cumplimiento de promesa de entrega |
| `mart_correlacion_otd_cpo` | ⭐ Cuánto sube CPO cuando OTD baja |
| `mart_devoluciones_motivo` | Devoluciones prevenibles |
| `mart_kpis_contact_center` | SLA, AHT, FCR, abandono, CSAT |
| `mart_alerts_diarias` | KPIs fuera de rango con owner P1/P2 |

**Insight estrella esperado:** cuando OTD < 90%, CPO sube de ~0.3 a ~0.7.
Documentar en `docs/insights.md`.

---

## 10. Reglas específicas para módulos no implementados

### 10.1 Antes de iniciar el Módulo 0

- Confirmar con el usuario.
- Crear `pyproject.toml` con `uv init`.
- Configurar Ruff + mypy + pre-commit + GitHub Actions ANTES de
  cualquier código funcional.
- Validar que `uv run ruff check .` y `uv run mypy .` pasen en un
  proyecto vacío.

### 10.2 Antes de iniciar cualquier módulo funcional (1-6)

- Verificar que el Módulo 0 está cerrado y CI está verde.
- Proponer al usuario el plan del módulo y esperar confirmación.
- Implementar paso a paso, pausando entre pasos.

### 10.3 Antes de iniciar M7 o M8 (post-MVP)

- Verificar que los módulos 1-6 están cerrados, el smoke test pasa,
  el CI está verde y los dashboards están publicados.
- Pedir confirmación explícita del usuario.

---

## 11. Estilo de interacción preferido por el usuario

El usuario (Julio) prefiere un estilo específico que **debe respetarse**:

- **Paso a paso, un concepto a la vez.** Nada de bloques masivos de
  código sin explicación previa.
- **Explicar el porqué antes de mostrar el código.**
  Contexto → decisión → código → verificación.
- **Pausar después de cada paso** para que el usuario lo ejecute antes
  de avanzar al siguiente.
- **No dar por sentado conocimiento previo** sobre infraestructura, GCP,
  herramientas. Si algo no se ha mencionado antes, explicar qué es.
- **Honestidad técnica sobre limitaciones:** si algo requiere tarjeta de
  crédito o setup adicional, decirlo de frente.
- **Respetar las decisiones de stack ya tomadas:** uv (no pip), dbt,
  Airflow local (no Cloud Composer), Ruff + mypy + pre-commit + CI.
- **Ofrecer alternativas cuando hay una restricción real**, no asumir
  que el usuario "encontrará la forma".

---

## 12. Anti-patrones a evitar

Estos son errores comunes que se han cometido antes en el proyecto y que
NO deben repetirse:

- ❌ Usar `pip install` en lugar de `uv add`.
- ❌ Crear archivos enormes de código sin pausar para explicar.
- ❌ Saltarse el Módulo 0 e ir directo a generadores.
- ❌ Hardcodear `PROJECT_ID` en el código.
- ❌ Asumir que el usuario tiene tarjeta de crédito o cuenta GCP de pago.
- ❌ Implementar tests "después" sin agregarlos en el módulo correspondiente.
- ❌ Commitear sin pasar por pre-commit.
- ❌ Subir `profiles.yml` con credenciales.
