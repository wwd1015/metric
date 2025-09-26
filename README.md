# 📊 Commercial Analytical Platform (CAP)

> *Streamlined metric development and deployment package with rich outputs*

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-00a99d.svg)](https://fastapi.tiangolo.com)
[![Plotly](https://img.shields.io/badge/Plotly-5.14+-3f4f75.svg)](https://plotly.com)

Commercial Analytical Platform (CAP) is a comprehensive Python package for developing, testing, and deploying complex analytics metrics with rich outputs including **DataFrames**, **interactive visualizations**, and **mixed object types**. Built specifically for **Posit Connect** deployment with streamlined development workflows.

## ✨ Key Features

- 🏗️ **Integrated Development**: Develop metrics within the package structure
- 📊 **Rich Outputs**: Support for DataFrames, Plotly charts, and complex objects  
- 🚀 **One-Click Deployment**: Ready-to-deploy Posit Connect scripts
- 🧪 **Interactive Testing**: Built-in dashboard and API for rapid development
- 📝 **Auto-Documentation**: YAML-driven configuration with type validation
- 🔧 **Template System**: Pre-built templates for common metric patterns
- 🧮 **Data Treatment Layer**: Unified utilities for fetching and transforming metric inputs from files or databases
- ⚡ **Polars Support**: Optional high-performance backend for bulk CSV/Parquet processing

## 📦 Package Structure

```
📁 cap/
├── 📁 cap/                    # 🏠 Main Package
│   ├── 📄 __init__.py                 # 📤 Package Exports
│   ├── 📄 core.py                     # 🔧 Metric Registry & Management
│   ├── 📄 api.py                      # 🌐 FastAPI Interface
│   ├── 📄 dashboard.py                # 📊 Interactive Dashboard
│   │
│   ├── 📁 metrics/                    # 📈 Metric Implementations
│   │   ├── 📄 __init__.py             # 📦 Metrics Package
│   │   ├── 📄 your_metric.py          # 🔍 Your Metric Code
│   │   └── 📄 your_metric.yaml        # ⚙️ Configuration File
│   │
│   └── 📁 scaffolding/                # 🛠️ Development Tools
│       ├── 📄 __init__.py             # 📦 Scaffolding Package
│       └── 📄 cli.py                  # 💻 Command Line Interface
│
├── 📁 tests/                          # 🧪 Test Suite
│   └── 📄 test_your_metric.py         # ✅ Generated Tests
│
├── 📁 deploy/                         # 🚀 Posit Connect Deployment Scripts
│   └── your_metric.py
├── 📄 pyproject.toml                  # ⚙️ Package Configuration
├── 📄 requirements.txt                # 📋 Dependencies
└── 📄 README.md                       # 📖 This File
```

## 🚀 Quick Start

### Installation

```bash
# Basic installation
pip install cap

# With all features (recommended for development)
pip install "cap[all]"

# Production deployment only
pip install "cap[api]"

# Add Polars-backed data treatment
pip install "cap[performance]"
```

### Create Your First Metric

```bash
# 1️⃣  Generate the YAML configuration
cap create "Sales Analysis" \
    --category financial \
    --description "Monthly sales performance analysis" \
    --template dataframe

# 2️⃣  Materialise Python/tests/deploy from the YAML when ready
cap generate financial_sales_analysis --overwrite-tests --overwrite-deploy

# 📁 Generated / updated files:
#   ├── cap/metrics/financial_sales_analysis.yaml
#   ├── cap/metrics/financial_sales_analysis.py
#   ├── tests/test_financial_sales_analysis.py
#   └── deploy/financial_sales_analysis.py
```

### Implement Your Metric

Open `cap/metrics/financial_sales_analysis.py` and replace the scaffolded placeholder
logic with your own between the `# --- CAP USER CODE START/END ---` markers. The CLI
preserves everything in that block each time you rerun `cap generate`, while refreshing
the function signature, docstring, and boilerplate derived from the YAML. Configuration
defaults live next door in the YAML file; keep it in sync with your function signature
(and rerun `cap generate` whenever you update the schema). The CLI also generates a
pytest file under `tests/` to get you started and a FastAPI deployment script under
`deploy/`. Required parameters in the YAML—such as `input_data` for the demo
calculator—must be supplied when calling the metric from any surface (CLI, API, or
Python) because no automatic fallback values are injected.

### Test Interactively

```bash
# Launch dashboard for testing
cap dashboard
# 🌐 Visit: http://localhost:8050

# Or start API server
cap api
# 🌐 Visit: http://localhost:8000/docs
```

### Orchestrate Metric Inputs

```python
from cap import CSVSource, SQLAlchemySource, DataTreatment

treatment = DataTreatment({
    "transactions": CSVSource("./data/transactions.csv"),
    "reference": SQLAlchemySource(
        connection_string="snowflake://user:pass@org-account/demo_db/public",
        query="SELECT code, label FROM reference_dim WHERE is_active = true",
    ),
})

treatment.add_transformer("transactions", lambda df: df[df["status"] == "COMPLETE"])

data_frames = treatment.load_many()
```

### Deploy to Posit Connect

```bash
# Test deployment locally
python deploy/financial_sales_analysis.py

# Deploy to Posit Connect
rsconnect deploy fastapi deploy/financial_sales_analysis.py \
    --account myaccount \
    --title "Sales Analysis API"
```

## 🎯 Use Cases & Templates

Each `cap create` command below writes only the YAML skeleton. Edit the configuration and
call `cap generate <metric_id>` when you are ready to materialise the Python module,
tests, and deployment helper.

### 📊 DataFrame Analytics
Perfect for data analysis and reporting:
```bash
cap create "Portfolio Performance" \
    --template dataframe \
    --category investment
```

### 📈 Interactive Visualizations  
For dashboard-ready charts:
```bash
cap create "Market Trends" \
    --template plotly \
    --category operational
```

### 🔗 Multi-Source Analytics
For comprehensive analysis:
```bash
cap create "Risk Assessment" \
    --template multi_source \
    --category risk
```

### ⚡ Simple Calculations
For quick numeric metrics:
```bash
cap create "KPI Calculator" \
    --template simple \
    --category performance
```

## 🛠️ Advanced Features

### Rich Output Types

Commercial Analytical Platform (CAP) supports multiple output formats automatically:

```python
# 📊 DataFrame → JSON/HTML/CSV
return pd.DataFrame({'portfolio': ['A', 'B'], 'return': [0.12, 0.08]})

# 📈 Plotly Figure → JSON/HTML/Interactive
return px.scatter(df, x='risk', y='return', title='Risk vs Return')

# 🎯 Mixed Objects → Structured Response
return {
    'analysis': dataframe,      # Table format
    'chart': plotly_figure,     # Interactive chart
    'metrics': {'roi': 0.15}    # Key numbers
}
```

### API Endpoints

Each metric automatically gets multiple endpoints:

```bash
# 📋 List all metrics
GET /metrics

# 📊 Calculate metric (JSON)
POST /calculate
{
  "metric_id": "financial_sales_analysis",
  "inputs": {"data_source": "...", "date_range": {...}}
}

# 🌐 Get HTML report
GET /calculate/financial_sales_analysis/html?param1=value1

# 💾 Download CSV
GET /calculate/financial_sales_analysis/csv?param1=value1
```

### Configuration-Driven Development

YAML configuration drives input validation and documentation:

```yaml
# cap/metrics/financial_sales_analysis.yaml
id: financial_sales_analysis
name: Sales Analysis
description: Monthly sales performance analysis
category: financial

inputs:
  - name: data_source
    type: string
    required: true
    description: Database connection string
  
  - name: date_range
    type: object
    required: true
    description: Start and end dates
    
  - name: filters
    type: object
    required: false
    description: Additional filters

outputs:
  - name: sales_data
    type: dataframe
    description: Sales data table
    
  - name: trend_chart
    type: plotly_figure
    description: Interactive trend chart
    
  - name: summary_stats
    type: object
    description: Key performance metrics
```

## 🎮 Interactive Development

### Dashboard Testing

The built-in dashboard provides:
- 🎛️ **Dynamic Forms**: Auto-generated input controls
- 📊 **Live Results**: Real-time metric calculation  
- 🔍 **Rich Display**: Tables, charts, and mixed outputs
- 🐛 **Debug Tools**: Error handling and logging

```bash
cap dashboard --debug
```

### API Development

Test your metrics with the interactive API:
- 📚 **Auto-Documentation**: OpenAPI/Swagger interface
- 🧪 **Live Testing**: Built-in request/response testing
- 📝 **Type Validation**: Automatic input/output validation
- 🔄 **Hot Reload**: Development mode with auto-restart

```bash  
cap api --reload
```

## 🚀 Deployment Options

### Posit Connect (Primary)

Generated deployment scripts work out-of-the-box:

```python
# deploy/your_metric.py
from cap.api import create_api_app
from cap.metrics.your_metric import calculate_your_metric

app = create_api_app()

# Custom endpoints, environment configuration, etc.
```

### Standalone Deployment

Deploy anywhere with standard FastAPI/Uvicorn:

```bash
# Docker
FROM python:3.11
COPY . .
RUN pip install cap
CMD ["uvicorn", "deploy/your_metric:app", "--host", "0.0.0.0"]

# Kubernetes, Cloud Run, Lambda, etc.
```

## 📚 Documentation

- 📖 **[User Guide](docs/user-guide.md)**: Development and deployment workflows
- 🏗️ **[Architecture](docs/architecture.md)**: System design and extensibility notes
- 🧪 **[Testing Guide](tests/README.md)**: Testing strategies and examples

## 🤝 Development Workflow

```mermaid
graph LR
    A[Create Metric] --> B[Implement Logic]
    B --> C[Test Dashboard]
    C --> D[Test API]
    D --> E[Run Tests]
    E --> F[Deploy]
    
    C --> B
    D --> B
```

1. **📝 Configure**: `cap create` to scaffold and refine the YAML inputs/outputs
2. **🔁 Materialise**: `cap generate` to sync Python/tests/deploy with the YAML
3. **🔧 Implement**: Add your calculation logic within the user-code markers
4. **🧪 Test**: Use dashboard and API for interactive development
5. **✅ Validate**: Run generated test suite
6. **🚀 Deploy**: Use generated deployment script for Posit Connect

## 🔧 CLI Reference

```bash
# Metric Management
cap create NAME [OPTIONS]     # Create new metric
cap generate METRIC_ID [OPTIONS]  # Materialise implementation from YAML config
cap list                      # List all metrics

# Development Tools  
cap dashboard [OPTIONS]       # Launch testing dashboard
cap api [OPTIONS]             # Launch API server

# Help & Information
cap --help                    # Show help
cap COMMAND --help            # Command-specific help
```

### Create Options

```bash
cap create "My Metric" \
    --category CATEGORY \              # Metric category
    --description TEXT \               # Metric description  
    --template TYPE \                  # Template: simple|dataframe|plotly|multi_source
    --complex \                        # Enable complex outputs
    --interactive                      # Interactive parameter setup
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Test specific metric
pytest tests/test_your_metric.py

# Test with coverage
pytest --cov=cap --cov-report=html

# Integration tests
pytest tests/integration/
```

## 📋 Requirements

- **Python**: 3.11+
- **Core**: pandas, numpy, pyyaml, click
- **API**: fastapi, uvicorn, pydantic  
- **Visualization**: plotly
- **Dashboard**: dash (optional)
- **Database**: sqlalchemy (optional)

## 🚨 Common Use Cases

### Financial Analytics
```python
@register_metric("portfolio_performance")
def calculate_portfolio_performance(portfolio_id: str, benchmark: str):
    # Load portfolio and benchmark data
    # Calculate returns, risk metrics, attribution
    return {
        'performance_chart': plotly_chart,
        'metrics_table': performance_df,
        'summary': {'sharpe': 1.2, 'alpha': 0.03}
    }
```

### Operational Metrics
```python
@register_metric("system_health")  
def calculate_system_health(time_range: dict, services: list):
    # Query monitoring data
    # Analyze performance, errors, capacity
    return {
        'health_dashboard': interactive_dashboard,
        'alert_summary': alerts_df,
        'recommendations': action_items
    }
```

### Business Intelligence
```python
@register_metric("sales_forecast")
def calculate_sales_forecast(region: str, product: str, horizon: int):
    # Load historical sales data
    # Apply forecasting models
    # Generate confidence intervals
    return {
        'forecast_chart': forecast_visualization,
        'historical_data': sales_df,
        'model_metrics': {'mae': 0.05, 'r2': 0.92}
    }
```

## 🆘 Troubleshooting

### Common Issues

❌ **Import Errors**
```bash
# Ensure cap is installed
pip install cap

# Check Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

❌ **Database Connections**
```python
# Test connections separately
import sqlalchemy as sa
engine = sa.create_engine(connection_string)
with engine.connect() as conn:
    result = conn.execute(sa.text("SELECT 1"))
```

❌ **Plotly Rendering**
```python
# Ensure proper figure creation
import plotly.graph_objects as go
fig = go.Figure()  # Not go.Figure
fig.add_trace(go.Scatter(x=[1,2,3], y=[1,2,3]))
```

### Debug Mode

```bash
# Enable verbose logging
cap dashboard --debug

# Check API responses  
curl -v http://localhost:8000/calculate/your_metric_id/html
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙋‍♀️ Support

- 📧 **Email**: support@metricshub.dev
- 💬 **Issues**: [GitHub Issues](https://github.com/yourusername/cap/issues)
- 📖 **Documentation**: [Full Documentation](https://cap.readthedocs.io/)

---

<div align="center">
<b>🚀 Start building powerful metrics today with Commercial Analytical Platform (CAP)! 🚀</b>
</div>
