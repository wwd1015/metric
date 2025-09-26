# Commercial Analytical Platform (CAP) User Guide

This guide covers the day-to-day workflows for building, testing, and deploying metrics with Commercial Analytical Platform (CAP). It complements the project README by diving deeper into the command-line tools and runtime surfaces you will use most often.

## 1. Installation

```bash
# Core features
pip install cap

# Development extras (dashboard, database connectors, tests)
pip install "cap[dashboard,database,api,dev]"
```

Verify your installation with `cap --help`.

## 2. Create a Metric

Start by generating a YAML configuration. This stage is non-destructive and can be rerun as you iterate on the schema:

```bash
cap create "Sales Analysis" \
    --category financial \
    --description "Monthly sales performance analysis" \
    --template dataframe
```

Flags to know:

- `--template`: one of `simple`, `dataframe`, `plotly`, or `multi_source`
- `--complex`: generate a multi-output scaffold
- `--interactive`: walk through prompts for inputs, outputs, and data sources

The command writes `cap/metrics/<metric>.yaml` and leaves implementation files untouched so you can refine the configuration first. Once the YAML is ready, materialise (or refresh) the Python module, tests, and deployment helper:

```bash
cap generate financial_sales_analysis --overwrite-tests --overwrite-deploy
```

`cap generate` reads the YAML, rebuilds the function signature and config-driven boilerplate, and preserves the code wrapped between the `# --- CAP USER CODE START/END ---` markers. Re-run it anytime you adjust inputs/outputs to keep interfaces in sync.

## 3. Edit and Run Metrics

Metric implementations live in `cap/metrics/<metric>.py` and are decorated with `@register_metric`. Configuration metadata is stored next to the implementation as YAML and is automatically picked up by the registry.

To execute a metric directly in Python:

```python
import polars as pl

from cap import CSVSource, SQLAlchemySource, DataTreatment, call_metric

treatment = DataTreatment(
    {
        "transactions": CSVSource("./data/transactions.csv", backend="polars"),
        "reference": SQLAlchemySource(
            connection_string="snowflake://user:pass@account/db/schema",
            query="SELECT code, label FROM dim_reference WHERE is_active",
        ),
    }
)

# Normalise input before the metric runs
import pandas as pd

def normalize_transactions(df):
    if pl is not None and isinstance(df, pl.DataFrame):
        return (
            df.filter(pl.col("status") == "COMPLETE")
              .with_columns(pl.col("amount").cast(pl.Float64))
        )
    df = pd.DataFrame(df)
    df = df[df["status"] == "COMPLETE"]
    df["amount"] = df["amount"].astype(float)
    return df

treatment.add_transformer("transactions", normalize_transactions)

data_frames = treatment.load_many()

transactions = data_frames["transactions"]
if pl is not None and isinstance(transactions, pl.DataFrame):
    input_sequence = transactions["amount"].to_list()
else:
    transactions = pd.DataFrame(transactions)
    input_sequence = transactions["amount"].tolist()

call_metric("demo_simple_calculator", input_data=input_sequence)
```

Polars support is optional. Install with `pip install "cap[performance]"` to enable the high-performance backend and ensure `polars` imports succeed at runtime. If the extra is missing, CAP gracefully falls back to pandas.

`cap/metrics/demo_simple_calculator.yaml` publishes the same `input_data` and `operation` parameters so the CLI wizard, API surface, and registry defaults stay in sync with the function signature. Because `input_data` is required, every surface (CLI, API, notebook) will reject calls that omit it, preventing accidental fallbacks.

## 4. Data Treatment Workflow

Use the `DataTreatment` layer whenever a metric needs to hydrate inputs from files or databases:

- **Declare sources** in the constructor (CSV, Parquet, SQL, API) and pick the backend (`pandas` by default, `polars` for large datasets).
- **Attach transformers** with `add_transformer` to normalise schemas, filter rows, or enrich data before execution. The example above keeps a single `normalize_transactions` function that works with either backend.
- **Load and call the metric** via `load_many()`; you receive a dictionary of data frames that can be passed directly to `call_metric` or your metric function.

The same flow underpins the `cap demo` notebook and the CLI scaffolds, so custom metrics stay consistent with how example content consumes the data treatment layer.

## 5. Test and Iterate

Each generated metric includes a pytest suite. Run targeted tests during development:

```bash
pytest tests/test_financial_sales_analysis.py
```

For the demo calculator metric already in the repo:

```bash
pytest tests/test_demo_simple_calculator.py
```

The rebuilt tests cover:
- happy-path execution and output typing
- validation and error handling
- API and dashboard integration (auto-skipped if optional deps are missing)

## 6. Interactive Surfaces

Launch the Dash-based testing dashboard:

```bash
cap dashboard --host 0.0.0.0 --port 8050
```

Start the FastAPI service for programmatic access:

```bash
cap api --reload
```

Explore the automatically generated docs at `http://localhost:8000/docs`.

## 7. Deploy to Posit Connect

Each scaffold includes a `deploy/<metric>.py` file. Deploy with the Posit CLI once dependencies are installed:

```bash
rsconnect deploy fastapi deploy/financial_sales_analysis.py \
    --account myaccount \
    --title "Sales Analysis API"
```

## 8. Best Practices

- Keep YAML configuration in sync with function signatures.
- Leverage the data treatment module for consistent preprocessing across metrics.
- Prefer writing integration tests that import the public API (`call_metric`, `create_api_app`) rather than touching internals.
- Use optional dependency extras (`dashboard`, `database`, `api`, `dev`) to match the runtime surface you need.

For architectural details see [`docs/architecture.md`](architecture.md).
