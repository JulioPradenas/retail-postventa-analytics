# Retail Postventa Analytics

<!-- CI badge — agregar después de crear el repo en GitHub:
![CI](https://github.com/<tu-usuario>/retail-postventa-analytics/actions/workflows/ci.yml/badge.svg)
-->

Proyecto de portafolio de Data Analyst. Analítica end-to-end de postventa
e-commerce retail LATAM (inspirado en Lider.cl / Walmart Chile). Datos 100% sintéticos.

**Pregunta de negocio:**
> ¿Cuántos contactos genera cada orden de e-commerce, por qué motivos,
> y cómo podemos predecir y reducir los contactos evitables?

**Insight estrella:** cuando OTD (On-Time Delivery) cae bajo el 90%, el CPO
(Contacts Per Order) sube de ~0.3 a ~0.7. Prevenir un retraso de despacho
equivale a prevenir dos contactos al contact center.

## Stack

| Capa | Tecnología |
|---|---|
| Lenguaje | Python 3.11+ |
| Gestor de paquetes | uv |
| Storage | BigQuery |
| Transformación | dbt-bigquery |
| Visualización | Looker Studio + Power BI |
| Calidad | Ruff + mypy + pytest + pre-commit + GitHub Actions |

## Comandos frecuentes

```bash
# Instalar dependencias
uv sync

# Linting + formato
uv run ruff check .
uv run ruff format .

# Type checking
uv run mypy .

# Tests
uv run pytest
```

## Estructura del proyecto

Ver `PROJECT_PLAN.md` para el plan completo de módulos y arquitectura.
