"""Tests estructurales del DAG de Airflow."""

from airflow.models import DAG, DagBag

DAG_ID = "retail_postventa_pipeline"
EXPECTED_TASKS = [
    "generate_orders",
    "generate_shipments",
    "generate_contacts",
    "generate_returns",
    "generate_surveys",
    "load_bigquery",
    "dbt_run",
    "dbt_test",
    "ml_predict",
]


def get_dag() -> DAG:
    bag = DagBag(dag_folder="orchestration/dags", include_examples=False)
    return bag.dags[DAG_ID]


def test_dag_loads_without_errors() -> None:
    bag = DagBag(dag_folder="orchestration/dags", include_examples=False)
    assert DAG_ID in bag.dags
    assert bag.import_errors == {}


def test_dag_has_expected_tasks() -> None:
    dag = get_dag()
    task_ids = {t.task_id for t in dag.tasks}
    assert task_ids == set(EXPECTED_TASKS)


def test_dag_task_count() -> None:
    dag = get_dag()
    assert len(dag.tasks) == len(EXPECTED_TASKS)


def test_dag_no_schedule() -> None:
    dag = get_dag()
    assert dag.schedule_interval is None


def test_dag_pipeline_order() -> None:
    """ml_predict debe ser el último task (downstream de dbt_test)."""
    dag = get_dag()
    ml_task = dag.get_task("ml_predict")
    upstream_ids = {t.task_id for t in ml_task.upstream_list}
    assert "dbt_test" in upstream_ids
