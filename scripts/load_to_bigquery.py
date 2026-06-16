"""Load synthetic CSV files into BigQuery raw tables.

Usage:
    export GCP_PROJECT_ID=<project>
    export GCP_BQ_DATASET=retail_postventa
    uv run python scripts/load_to_bigquery.py

Idempotent: dataset creation catches Conflict; tables are WRITE_TRUNCATE.
"""

import os
from pathlib import Path

import pandas as pd
from google.cloud import bigquery
from google.cloud.exceptions import Conflict

_CSV_DIR = Path("data_gen/csv")

_TABLE_MAP: dict[str, Path] = {
    "raw_orders": _CSV_DIR / "orders.csv",
    "raw_shipments": _CSV_DIR / "shipments.csv",
    "raw_contacts": _CSV_DIR / "contacts.csv",
    "raw_returns": _CSV_DIR / "returns.csv",
    "raw_surveys": _CSV_DIR / "surveys.csv",
}


def get_env(name: str) -> str:
    """Read a required environment variable.

    Args:
        name: Variable name.

    Returns:
        Variable value.

    Raises:
        ValueError: If the variable is not set or empty.
    """
    value = os.environ.get(name, "")
    if not value:
        raise ValueError(f"Environment variable {name} is not set. Export it before running.")
    return value


def create_dataset_if_not_exists(client: bigquery.Client, dataset_id: str) -> None:
    """Create a BigQuery dataset if it does not already exist.

    Args:
        client: Authenticated BigQuery client.
        dataset_id: Dataset name (without project prefix).
    """
    dataset_ref = bigquery.Dataset(f"{client.project}.{dataset_id}")
    dataset_ref.location = "US"
    try:
        client.create_dataset(dataset_ref)
        print(f"  Created dataset: {dataset_id}")
    except Conflict:
        print(f"  Dataset already exists: {dataset_id}")


def load_csv_to_table(
    client: bigquery.Client,
    project_id: str,
    dataset_id: str,
    table_name: str,
    csv_path: Path,
) -> None:
    """Load a CSV into a BigQuery table, truncating if it already exists.

    Args:
        client: Authenticated BigQuery client.
        project_id: GCP project ID.
        dataset_id: Target dataset name.
        table_name: Target table name.
        csv_path: Path to the source CSV file.
    """
    table_ref = f"{project_id}.{dataset_id}.{table_name}"
    df: pd.DataFrame = pd.read_csv(csv_path)

    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        autodetect=True,
    )

    job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)
    job.result()
    print(f"  {table_name}: {len(df):,} rows → {table_ref}")


def main() -> None:
    """Create dataset and load all 5 CSV files to BigQuery raw layer."""
    project_id = get_env("GCP_PROJECT_ID")
    dataset_id = get_env("GCP_BQ_DATASET")

    print(f"Project : {project_id}")
    print(f"Dataset : {dataset_id}")

    client = bigquery.Client(project=project_id)
    create_dataset_if_not_exists(client, dataset_id)

    print("\nLoading tables:")
    for table_name, csv_path in _TABLE_MAP.items():
        load_csv_to_table(client, project_id, dataset_id, table_name, csv_path)

    print("\nDone. 5 raw tables loaded to BigQuery.")


if __name__ == "__main__":
    main()
