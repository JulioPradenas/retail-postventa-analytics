# Module 0: Setup Base + Tooling de Calidad — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Initialize the retail-postventa-analytics repo with git, uv, Ruff, mypy, pytest, pre-commit, and GitHub Actions CI so every future commit is enforced to be clean before any functional code is written.

**Architecture:** Single Python project managed by uv. All quality tools (Ruff, mypy, pytest) are dev dependencies installed via `uv add --dev`. Pre-commit runs Ruff + mypy before every local commit. GitHub Actions mirrors the same checks on every push and PR. Zero functional code in this module — only scaffolding and tooling.

**Tech Stack:** Python 3.11+, uv, Ruff (lint + format), mypy strict, pytest, pre-commit, GitHub Actions.

---

### Task 1: Initialize git repository

**Files:**
- Create: `.git/` (via `git init`)

- [ ] **Step 1: Initialize git and set main branch**

```bash
git init
git branch -M main
```

Expected output:
```
Initialized empty Git repository in .../Retail Postventa Analytics/.git/
```

- [ ] **Step 2: Verify state**

```bash
git status
```

Expected: `On branch main — No commits yet — nothing to commit`

---

### Task 2: Initialize uv project

**Files:**
- Create: `pyproject.toml`
- Create: `.python-version`
- Delete: `hello.py` (sample file created by uv — not needed)

> **Contexto:** `uv init` es el comando que inicializa un proyecto Python gestionado por uv. Genera `pyproject.toml` (el equivalente moderno de `setup.py`) y `hello.py` (un script de ejemplo que eliminaremos). El flag `--name` fuerza el nombre del paquete porque el directorio tiene espacios.

- [ ] **Step 1: Init uv project with explicit package name**

```bash
uv init --name retail-postventa-analytics
```

Expected output:
```
Initialized project `retail-postventa-analytics`
```

- [ ] **Step 2: Remove sample file created by uv**

```bash
rm hello.py
```

Expected: file deleted silently (no output).

- [ ] **Step 3: Verify pyproject.toml content**

```bash
cat pyproject.toml
```

Expected: file with `[project]` section, `name = "retail-postventa-analytics"`, `requires-python = ">=3.11"`.

---

### Task 3: Add dev dependencies

**Files:**
- Modify: `pyproject.toml` (uv adds `[dependency-groups]` section automatically)
- Create: `uv.lock`

> **Contexto:** `uv add --dev` agrega dependencias de desarrollo al proyecto. Nunca usar `pip install`. uv genera `uv.lock` que se versiona para reproducibilidad exacta.

- [ ] **Step 1: Install all dev dependencies in one command**

```bash
uv add --dev ruff mypy pytest pre-commit
```

Expected: uv resolves and installs packages, creates `uv.lock`. Output will show package resolution.

- [ ] **Step 2: Verify tools are available via uv**

```bash
uv run ruff --version && uv run mypy --version && uv run pytest --version
```

Expected: version numbers printed for each (e.g., `ruff 0.x.x`, `mypy x.x.x`, `pytest x.x.x`). No errors.

---

### Task 4: Configure Ruff and mypy in pyproject.toml

**Files:**
- Modify: `pyproject.toml` (add `[tool.ruff]`, `[tool.ruff.lint]`, `[tool.mypy]`, update `description`)

- [ ] **Step 1: Update description and add tool config sections**

Open `pyproject.toml` and make two edits:

**Edit 1** — update the `description` field in `[project]`:
```toml
description = "Analítica end-to-end de postventa e-commerce retail LATAM"
```

**Edit 2** — append these sections at the end of the file:
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

[tool.mypy]
python_version = "3.11"
strict = true
ignore_missing_imports = true
warn_unused_ignores = true
```

- [ ] **Step 2: Validate Ruff lint**

```bash
uv run ruff check .
```

Expected: `All checks passed!`

- [ ] **Step 3: Validate Ruff format**

```bash
uv run ruff format --check .
```

Expected: `All files are already formatted` or `1 file left unchanged`

- [ ] **Step 4: Validate mypy**

```bash
uv run mypy .
```

Expected: `Success: no issues found in 0 source files`

---

### Task 5: Create .gitignore

**Files:**
- Create: `.gitignore`

- [ ] **Step 1: Create .gitignore with this exact content**

```gitignore
# Python
__pycache__/
*.py[cod]
*.pyo
*.pyd
*.so

# uv / virtualenv
.venv/
*.egg-info/
dist/
build/

# Testing
.pytest_cache/
.coverage
htmlcov/

# mypy
.mypy_cache/

# dbt
dbt_project/dbt_packages/
dbt_project/target/
dbt_project/logs/
dbt_project/profiles.yml

# GCP / credenciales — NUNCA versionar
.env
.env.*
service-account*.json
GOOGLE_APPLICATION_CREDENTIALS

# Data generada (outputs de data_gen/)
data_gen/csv/

# MacOS
.DS_Store

# IDEs
.vscode/
.idea/
```

- [ ] **Step 2: Verify .venv is ignored**

```bash
git status
```

Expected: `.gitignore` appears as untracked. `.venv/` does NOT appear in the list (it is correctly ignored).

---

### Task 6: Create .pre-commit-config.yaml

**Files:**
- Create: `.pre-commit-config.yaml`

> **Contexto:** pre-commit ejecuta hooks automáticamente antes de cada `git commit`. Usamos hooks `local` que llaman a `uv run` para garantizar que siempre se usa la versión del proyecto, no una global del sistema.

- [ ] **Step 1: Create config**

```yaml
repos:
  - repo: local
    hooks:
      - id: ruff-check
        name: ruff (lint)
        entry: uv run ruff check --fix
        language: system
        types: [python]
        pass_filenames: false

      - id: ruff-format
        name: ruff (format)
        entry: uv run ruff format
        language: system
        types: [python]
        pass_filenames: false

      - id: mypy
        name: mypy
        entry: uv run mypy .
        language: system
        types: [python]
        pass_filenames: false
```

- [ ] **Step 2: Install hooks into git**

```bash
uv run pre-commit install
```

Expected: `pre-commit installed at .git/hooks/pre-commit`

- [ ] **Step 3: Run hooks on all files to verify**

```bash
uv run pre-commit run --all-files
```

Expected: all three hooks show `Passed`. Example output:
```
ruff (lint)..................................................................Passed
ruff (format)................................................................Passed
mypy.........................................................................Passed
```

---

### Task 7: Create GitHub Actions CI workflow

**Files:**
- Create: `.github/workflows/ci.yml`

> **Contexto:** GitHub Actions ejecuta los mismos checks que pre-commit (Ruff + mypy + pytest) en la nube en cada push y PR. El badge en el README mostrará verde cuando todo pase.

- [ ] **Step 1: Create directory**

```bash
mkdir -p .github/workflows
```

- [ ] **Step 2: Create ci.yml**

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  quality:
    name: Lint, Type Check, Test
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install uv
        uses: astral-sh/setup-uv@v4

      - name: Install dependencies
        run: uv sync --all-extras

      - name: Lint with Ruff
        run: uv run ruff check .

      - name: Check formatting with Ruff
        run: uv run ruff format --check .

      - name: Type check with mypy
        run: uv run mypy .

      - name: Run tests
        run: uv run pytest
```

- [ ] **Step 3: Verify file is valid YAML**

```bash
uv run python -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml')); print('YAML válido')"
```

Expected: `YAML válido`

Note: `yaml` is part of Python's stdlib (`PyYAML` is included via other deps). If not available, install with `uv add --dev pyyaml`.

---

### Task 8: Create README.md

**Files:**
- Modify: `README.md` (uv init may have created a stub — overwrite it)

> **Nota sobre el badge CI:** el badge requiere la URL del repositorio de GitHub, que no existe todavía. Se agrega manualmente después de hacer `git push` y crear el repo en GitHub. El formato es:
> `![CI](https://github.com/<usuario>/<repo>/actions/workflows/ci.yml/badge.svg)`

- [ ] **Step 1: Write README.md**

```markdown
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
```

---

### Task 9: Create tests structure

**Files:**
- Create: `tests/__init__.py` (empty file)

- [ ] **Step 1: Create empty tests package**

Create an empty file at `tests/__init__.py`. No content needed — it just tells Python that `tests/` is a package pytest can discover.

- [ ] **Step 2: Verify pytest runs without errors**

```bash
uv run pytest
```

Expected output:
```
============== no tests ran ==============
```

Zero errors, zero failures. Just no tests yet — that is correct for M0.

---

### Task 10: Final smoke test + first commit

**Files:**
- Commit: all files created above

- [ ] **Step 1: Run full quality smoke test**

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy .
uv run pytest
```

All four commands must exit with code 0 (no errors). If any fails, fix it before proceeding.

- [ ] **Step 2: Verify no sensitive files will be committed**

```bash
git status
```

Confirm that these are NOT in the list: `.venv/`, `.env`, `*.json`, `profiles.yml`.

- [ ] **Step 3: Stage all project files**

```bash
git add pyproject.toml uv.lock .gitignore .pre-commit-config.yaml .python-version README.md .github/workflows/ci.yml tests/__init__.py docs/superpowers/plans/2026-06-16-module-0-setup.md
```

- [ ] **Step 4: Commit (pre-commit hooks run automatically)**

```bash
git commit -m "chore: M0 — setup base + tooling de calidad"
```

Expected: pre-commit hooks fire (ruff + mypy), all pass, commit succeeds with message shown.

- [ ] **Step 5: Verify commit exists**

```bash
git log --oneline
```

Expected: one line — `<hash> chore: M0 — setup base + tooling de calidad`

---

## Self-Review

**Spec coverage (PROJECT_PLAN.md §9.1):**
- `pyproject.toml` con uv ✓ Task 2+3
- `uv.lock` versionado ✓ Task 3
- Ruff config en pyproject.toml ✓ Task 4
- mypy config en pyproject.toml ✓ Task 4
- `.pre-commit-config.yaml` con Ruff + mypy ✓ Task 6
- `.github/workflows/ci.yml` ✓ Task 7
- Badge CI en README — ⚠️ **Gap conocido:** requiere URL del repo GitHub, que no existe al momento de implementar. Agregar manualmente después de `git push` (comentario incluido en README de Task 8).
- `.gitignore` ✓ Task 5

**Gaps:** ninguno bloqueante. El badge CI se agrega post-push.
