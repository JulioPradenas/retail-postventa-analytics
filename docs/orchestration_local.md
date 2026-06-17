# Orquestación Local — Airflow (M8)

Guía para correr el DAG `retail_postventa_pipeline` con Airflow standalone en
local. El pipeline ejecuta la secuencia completa: generación de datos sintéticos
→ carga a BigQuery → dbt (`run` + `test`) → modelo predictivo.

> El `AIRFLOW_HOME` del proyecto (`orchestration/airflow/`) está en `.gitignore`,
> por lo que la configuración y el shim descritos abajo **no se versionan** y hay
> que recrearlos una vez en cada máquina.

---

## 1. Variables y arranque

```bash
cd "/ruta/a/Retail Postventa Analytics"

export AIRFLOW_HOME="$PWD/orchestration/airflow"
export PATH="$PWD/.venv/bin:$PATH"
export PYTHONPATH="$PWD/orchestration/airflow/shims:$PWD"
export GCP_PROJECT_ID="<tu-proyecto-bq>"
export GCP_BQ_DATASET="retail_postventa"

# Workarounds de fork en macOS (ver sección 3)
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
export no_proxy="*"

airflow standalone
```

UI en <http://localhost:8080>. Usuario `admin`; la contraseña se genera en
`orchestration/airflow/standalone_admin_password.txt`.

Disparar el pipeline:

```bash
airflow dags unpause retail_postventa_pipeline
airflow dags trigger retail_postventa_pipeline
```

---

## 2. Configuración requerida en `airflow.cfg`

Dentro de `orchestration/airflow/airflow.cfg`:

| Clave | Valor | Por qué |
|---|---|---|
| `dags_folder` | `.../orchestration/dags` | Donde vive el DAG (no el default `$AIRFLOW_HOME/dags`). |
| `load_examples` | `False` | Los ~60 DAGs de ejemplo saturan el parseo, disparan timeouts del DagFileProcessor y dejan tareas huérfanas. |
| `execute_tasks_new_python_interpreter` | `True` | Lanza un intérprete nuevo por tarea en vez de `fork` (más robusto en macOS). |

---

## 3. Workaround del segfault de `setproctitle` (macOS)

En macOS moderno (Apple Silicon, macOS 26.x) la librería nativa `setproctitle`
provoca `SIGSEGV` al renombrar el proceso:

```
_setproctitle.cpython-311-darwin.so  darwin_set_process_title
  → CoreFoundation  CFBundleGetFunctionPointerForName
  → libsystem_trace.dylib  _os_log_preferences_refresh   ← crash
```

Esto mata **los workers de gunicorn** (la UI no carga) y **el task runner de
Airflow** (las tareas quedan en `running` sin ejecutarse). El diagnóstico está en
`~/Library/Logs/DiagnosticReports/python3.11-*.ips`.

Como `setproctitle` es puramente cosmético, se neutraliza con un shim no-op
antepuesto al `PYTHONPATH`. Crear `orchestration/airflow/shims/setproctitle.py`:

```python
"""No-op shim para setproctitle (evita SIGSEGV en macOS al renombrar el proceso)."""

from __future__ import annotations


def setproctitle(title: str | None = None) -> None:
    return None


def getproctitle() -> str:
    return ""


def setthreadtitle(title: str | None = None) -> None:
    return None


def getthreadtitle() -> str:
    return ""
```

Con `PYTHONPATH="$PWD/orchestration/airflow/shims:$PWD"` (sección 1) Airflow y
gunicorn importan este shim en lugar del binario nativo.

---

## 4. Notas del DAG

El DAG (`orchestration/dags/retail_postventa_dag.py`, sí versionado) ya contempla
que la ruta del proyecto puede tener espacios:

- Las rutas en cada `bash_command` van entre comillas (evita `exit 127` por
  word splitting de la ruta).
- Cada `BashOperator` usa `cwd=PROJECT_ROOT` para que los scripts resuelvan sus
  paths relativos (`data_gen/csv/…`) contra la raíz del proyecto.
- `append_env=True` hereda el entorno del scheduler (PATH, credenciales, etc.).
