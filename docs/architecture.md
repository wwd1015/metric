# Commercial Analytical Platform (CAP) Architecture

This document captures the key building blocks of the Commercial Analytical Platform (CAP) package and how they interact. It replaces the older `ARCHITECTURE.md` and `IMPLEMENTATION_GUIDE.md` files.

## 1. High-Level View

```
┌──────────────────────────────────────────────────────────────┐
│                      Commercial Analytical Platform (CAP) Package                     │
├──────────────────────────────────────────────────────────────┤
│  cap.core        – Metric registry and discovery     │
│  cap.metrics     – Metric implementations + configs  │
│  cap.api         – FastAPI surface with rich outputs │
│  cap.dashboard   – Dash UI for interactive testing   │
│  cap.data        – Data treatment sources/pipeline   │
│  cap.scaffolding – CLI for scaffolding + utilities   │
└──────────────────────────────────────────────────────────────┘
```

## 2. Package Structure (abridged)

```
cap/
├── __init__.py          # public exports and convenience imports
├── core.py              # MetricRegistry, registration helpers
├── api.py               # FastAPI app factory, result formatting
├── dashboard.py         # Dash app factory and callbacks
├── data/                # Source connectors and DataTreatment pipeline
├── metrics/             # User-authored metrics + YAML configs
└── scaffolding/cli.py   # `cap` command line interface
```

Tests live in `tests/` and deployment helpers are generated per metric under `deploy/<metric>.py`.

## 3. Metric Registry Workflow

1. `MetricRegistry` loads YAML configs and discovers functions marked with `@register_metric`.
2. Config defaults are merged with runtime parameters during `call_metric`.
3. The registry exposes helpers (`get_metric`, `list_metrics`, `call_metric`) via `cap.__init__`.

## 4. Runtime Surfaces

- **FastAPI (`cap.api`)**: converts metric results to JSON/HTML/CSV, supports GET and POST calculation endpoints, and powers deployment to Posit Connect.
- **Dash Dashboard (`cap.dashboard`)**: auto-generates forms from YAML metadata for rapid manual testing.
- **Data Treatment (`cap.data`)**: optional orchestration layer that fetches inputs from files or databases before handing them to a metric.

### Data Treatment Flow

The optional `cap.data` package adds an orchestration layer that sits in front of the
registry. A typical flow looks like this:

1. **Register sources** using `DataTreatment.register_source()` (or pass them to the
   constructor). Sources implement `BaseSource.fetch()` and can read from CSV/Parquet
   files or SQL databases. CSV/Parquet sources support a `backend` argument
   (`"pandas"` by default, `"polars"` for high-performance ingestion).
2. **Attach transformers** with `add_transformer()` to apply reusable cleanup or
   enrichment steps immediately after the raw fetch.
3. **Load data** with `load()` or `load_many()`. These return `pandas.DataFrame`
   objects ready to pass into a metric via `cap.call_metric()` or directly inside a
   service layer.

Because the registry simply executes metrics, you are free to orchestrate inputs using
`DataTreatment` anywhere in your application (FastAPI endpoints, background jobs, or
interactive notebooks).

### Built-in Sample Metric

- **`demo_simple_calculator`** – a lightweight demonstration metric that exercises
  defaults, validation, and mixed outputs. Useful for smoke-testing the registry, API,
  dashboard, or data treatment hookups without external data.
- Signature conventions: metrics accept `input_data` as the first parameter (a DataFrame
  with a canonical `value` column for numeric analysis) and expose additional knobs (for
  example `operation`) as keyword-only arguments. YAML `inputs` mirror those names so
  generated CLIs, APIs, and defaults stay aligned with the implementation.

## 5. Scaffolded Developer Experience

The CLI now separates configuration from code generation so workflows stay predictable:

- `cap create …` writes or refreshes the YAML configuration only, giving you a safe place
  to iterate on inputs/outputs without touching implementation files.
- `cap generate <metric_id>` reads the YAML, regenerates the Python module signature,
  pytest scaffold, and deployment stub, and preserves everything between the
  `# --- CAP USER CODE START/END ---` markers.

Additional commands expose `cap dashboard`, `cap api`, `cap list`, and `cap remove`.

## 6. Extensibility Notes

- Add new data connectors by subclassing `BaseSource` and registering them with `DataTreatment`.
- Extend the API or dashboard by building on `create_api_app()` and `create_dashboard_app()` factories.
- Template behaviour lives in `scaffolding/cli.py`; update `_get_template_config` and friends to influence generated code/tests.

For usage-oriented guidance see [`docs/user-guide.md`](user-guide.md).
