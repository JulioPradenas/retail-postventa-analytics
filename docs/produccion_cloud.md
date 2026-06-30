# Producción en la nube — Equivalencias por ecosistema

Anexo de arquitectura. El proyecto corre hoy en local (Airflow standalone +
BigQuery + dbt + scikit-learn). Este documento mapea cada componente a su
equivalente gestionado en GCP, AWS, Azure y Kubernetes, como referencia de
cómo se vería el pipeline `retail_postventa_pipeline` en producción.

---

## 1. Mapeo por componente

| Componente (este proyecto) | GCP | AWS | Azure | Kubernetes (cloud-agnóstico) |
|---|---|---|---|---|
| **Orquestador** (Airflow) | Cloud Composer | MWAA (Managed Workflows for Apache Airflow) | Managed Airflow (Data Factory) / Astronomer | Airflow (Helm) + `KubernetesExecutor` |
| **Data warehouse** (BigQuery) | BigQuery | Redshift / Athena | Synapse / Fabric | Trino / ClickHouse self-hosted |
| **Transformación** (dbt) | dbt-bigquery | dbt-redshift / dbt-athena | dbt-synapse / dbt-fabric | dbt-core en Pod / dbt Cloud |
| **Storage de raw** (CSVs) | Cloud Storage (GCS) | S3 | Blob Storage / ADLS Gen2 | MinIO (S3-compatible) |
| **Runtime de tareas** (executor) | Composer worker (GKE) | MWAA worker (Fargate) | Container Instances | Pods efímeros (1 por tarea) |
| **Metadata DB de Airflow** | Cloud SQL (Postgres) | Aurora Postgres | Azure DB for PostgreSQL | Postgres en el cluster |
| **Entrenar/servir ML** (sklearn) | Vertex AI | SageMaker | Azure ML | KServe / Seldon |
| **Secretos** (credenciales GCP) | Secret Manager | Secrets Manager / SSM | Key Vault | External Secrets / Sealed Secrets |
| **Scheduling/trigger** | Composer (cron) / Cloud Scheduler | MWAA (cron) / EventBridge | Data Factory triggers | CronJob / Airflow schedule |
| **Alertas** (`on_failure_callback`) | Cloud Monitoring + Pub/Sub→Slack | CloudWatch + SNS→Slack | Monitor + Action Groups | Alertmanager (Prometheus) |
| **CI/CD** (GitHub Actions) | Cloud Build | CodePipeline | Azure DevOps | Argo CD (GitOps) |

---

## 2. Airflow: las dos decisiones clave

### 2.1 Dónde corre Airflow

| Opción | Esfuerzo ops | Control | Cuándo conviene |
|---|---|---|---|
| Cloud Composer / MWAA | Bajo | Medio | La empresa ya vive en GCP/AWS; quieres olvidarte de la infra |
| Astronomer | Bajo | Alto | Multi-cloud; quieres soporte y buenas prácticas |
| Airflow en K8s (Helm) | Alto | Total | Hay equipo de plataforma; quieres portabilidad y costo controlado |

### 2.2 Qué Executor usa (reemplaza al `SequentialExecutor` local)

| Executor | Cómo corre las tareas | Paralelismo | Producción |
|---|---|---|---|
| `SequentialExecutor` | Una a la vez, mismo proceso | Ninguno | Solo local (estado actual) |
| `LocalExecutor` | Procesos en una sola máquina | Limitado a la VM | Equipos chicos |
| `CeleryExecutor` | Pool de workers fijos + cola (Redis) | Alto, workers siempre encendidos | Carga constante |
| `KubernetesExecutor` | Un Pod efímero por tarea | Elástico, escala a cero | Estándar moderno |

Con `KubernetesExecutor`, `dbt_run` arranca un Pod con la imagen de dbt, corre y
muere; `generate_orders` arranca otro Pod con la imagen de Python. Aislamiento
total y pago solo por lo usado.

---

## 3. Qué cambia (y qué no) en el DAG

El **código del DAG casi no cambia** — esa es la gracia de Airflow. Lo que cambia:

- Los `BashOperator` que llaman `.venv/bin/python` → **operators nativos del cloud**:
  - GCP: `BigQueryInsertJobOperator`, `DataprocSubmitJobOperator`, `KubernetesPodOperator`
  - AWS: `RedshiftDataOperator`, `GlueJobOperator`, `EcsRunTaskOperator`
  - Azure: `AzureSynapseRunSparkBatchOperator`, `AzureContainerInstancesOperator`
- Credenciales por env var (`GCP_PROJECT_ID`) → **Airflow Connections** apuntando al Secret Manager del cloud.
- El `cwd` y el shim de `setproctitle` (workarounds de macOS local) → **desaparecen**: se corre en imágenes Linux dentro de contenedores.

La lógica de dependencias, el `default_args` con `retries`/`on_failure_callback`
y el orden de las 9 tareas se mantienen intactos.

---

## 4. Recomendación para este proyecto

Como el stack ya es **BigQuery + dbt**, el camino de menor fricción es
**GCP + Cloud Composer**: Airflow gestionado sobre GKE (sin pelear con SQLite ni
`setproctitle`), operators nativos de BigQuery, y `KubernetesPodOperator` para
los generadores y el ML.

El stack más sólido de cara a una entrevista sería **Airflow en Kubernetes con
`KubernetesExecutor` + dbt + warehouse**: portable entre clouds y demuestra
dominio de la capa de infraestructura, no solo del DAG.
