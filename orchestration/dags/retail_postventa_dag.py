"""DAG principal del pipeline Retail Postventa Analytics.

Secuencia completa: generación de datos → carga BigQuery → dbt → ML.

Ejecución manual (no schedule) para uso como portafolio.
Para lanzar: airflow dags trigger retail_postventa_pipeline
"""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

from airflow import DAG
from airflow.operators.bash import BashOperator

PROJECT_ROOT = str(Path(__file__).parents[2])
PYTHON = f"{PROJECT_ROOT}/.venv/bin/python"
DBT_BIN = str(Path.home() / ".local/bin/dbt")  # uv tool install dbt-core
DBT_PROJECT_DIR = f"{PROJECT_ROOT}/dbt_project"
DBT_PROFILES_DIR = str(Path.home() / ".dbt")

_ENV = {
    "GCP_PROJECT_ID": os.environ.get("GCP_PROJECT_ID", ""),
    "GCP_BQ_DATASET": os.environ.get("GCP_BQ_DATASET", "retail_postventa"),
    "PYTHONPATH": PROJECT_ROOT,
}

with DAG(
    dag_id="retail_postventa_pipeline",
    description="Pipeline end-to-end: datos sintéticos → BigQuery → dbt → ML",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    tags=["retail", "postventa", "portfolio"],
) as dag:
    generate_orders = BashOperator(
        task_id="generate_orders",
        bash_command=f"{PYTHON} {PROJECT_ROOT}/data_gen/generar_orders.py",
        env=_ENV,
    )

    generate_shipments = BashOperator(
        task_id="generate_shipments",
        bash_command=f"{PYTHON} {PROJECT_ROOT}/data_gen/generar_shipments.py",
        env=_ENV,
    )

    generate_contacts = BashOperator(
        task_id="generate_contacts",
        bash_command=f"{PYTHON} {PROJECT_ROOT}/data_gen/generar_contacts.py",
        env=_ENV,
    )

    generate_returns = BashOperator(
        task_id="generate_returns",
        bash_command=f"{PYTHON} {PROJECT_ROOT}/data_gen/generar_returns.py",
        env=_ENV,
    )

    generate_surveys = BashOperator(
        task_id="generate_surveys",
        bash_command=f"{PYTHON} {PROJECT_ROOT}/data_gen/generar_surveys.py",
        env=_ENV,
    )

    load_bigquery = BashOperator(
        task_id="load_bigquery",
        bash_command=f"{PYTHON} {PROJECT_ROOT}/scripts/load_to_bigquery.py",
        env=_ENV,
    )

    _dbt_flags = f"--project-dir {DBT_PROJECT_DIR} --profiles-dir {DBT_PROFILES_DIR}"

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=f"{DBT_BIN} run {_dbt_flags}",
        env=_ENV,
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=f"{DBT_BIN} test {_dbt_flags}",
        env=_ENV,
    )

    ml_predict = BashOperator(
        task_id="ml_predict",
        bash_command=f"{PYTHON} {PROJECT_ROOT}/ml/predict_contact.py",
        env=_ENV,
    )

    # Generadores en secuencia: cada uno depende del CSV del anterior
    (
        generate_orders
        >> generate_shipments
        >> generate_contacts
        >> generate_returns
        >> generate_surveys
        >> load_bigquery
        >> dbt_run
        >> dbt_test
        >> ml_predict
    )
