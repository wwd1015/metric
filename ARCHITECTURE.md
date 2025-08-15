# 🏗️ Metrics Hub Architecture

## 🎯 Overview

Metrics Hub provides a streamlined architecture for developing, testing, and deploying complex metrics with rich outputs including DataFrames and interactive Plotly visualizations. The platform is optimized for **Posit Connect** deployment and supports **within-package metric development**.

## 🎨 Design Principles

- 🏗️ **Integrated Development**: Develop metrics within the package structure
- 📊 **Rich Outputs**: First-class support for DataFrames, Plotly charts, and mixed data structures
- 📝 **YAML-Driven**: Declarative metric configuration without code deployment
- 🚀 **Posit Connect Ready**: One-command deployment to Posit Connect
- 🛠️ **Developer Experience**: Smart scaffolding and comprehensive templates

## 🏛️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    🏠 METRICS HUB PACKAGE                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   📈 METRICS    │  │   🔧 CORE       │  │  🛠️ SCAFFOLDING │  │
│  │                 │  │                 │  │                 │  │
│  │ • your_metric.py│  │ • Registry      │  │ • CLI Tools     │  │
│  │ • config.yaml   │  │ • Discovery     │  │ • Templates     │  │
│  │ • Auto-Registry │  │ • Management    │  │ • Generators    │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
│           │                     │                     │          │
└───────────┼─────────────────────┼─────────────────────┼──────────┘
            │                     │                     │
            ▼                     ▼                     ▼
  ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
  │  🌐 API LAYER   │   │ 📊 DASHBOARD    │   │ 🚀 DEPLOYMENT  │
  │                 │   │                 │   │                 │
  │ • FastAPI       │   │ • Interactive   │   │ • Posit Connect │
  │ • Multiple      │   │ • Testing       │   │ • Auto Scripts  │
  │   Formats       │   │ • Debugging     │   │ • Environment   │
  │ • Rich Outputs  │   │ • Live Reload   │   │   Ready         │
  └─────────────────┘   └─────────────────┘   └─────────────────┘
```

## 🔧 Core Components

### 📦 Package Structure

```
📁 metrics-hub/
├── 📁 metrics_hub/                    # 🏠 Main Package
│   │
│   ├── 📄 __init__.py                 # 📤 Core Exports
│   │   ├── register_metric()          # 🏷️ Decorator Function  
│   │   ├── get_metric()               # 🔍 Metric Lookup
│   │   ├── list_metrics()             # 📋 Metric Discovery
│   │   ├── call_metric()              # ⚡ Execution Engine
│   │   ├── create_api_app()           # 🌐 API Factory
│   │   └── run_dashboard()            # 📊 Dashboard Launcher
│   │
│   ├── 📄 core.py                     # 🔧 Registry Engine
│   │   ├── MetricRegistry()           # 📚 Central Registry
│   │   ├── Auto-Discovery            # 🔍 Package Scanning
│   │   ├── YAML Configuration         # ⚙️ Config Management
│   │   └── Function Management        # 🎯 Execution Control
│   │
│   ├── 📄 api.py                      # 🌐 Web Interface
│   │   ├── FastAPI Application        # 🚀 Modern Web Framework
│   │   ├── Rich Output Processing     # 🎨 Format Conversion
│   │   ├── Multiple Endpoints         # 🔗 Access Patterns
│   │   └── Posit Connect Health       # 💚 Deployment Support
│   │
│   ├── 📄 dashboard.py                # 📊 Interactive Testing
│   │   ├── Dash Application           # 🎛️ Web Dashboard
│   │   ├── Dynamic Form Generation    # 📝 Auto UI
│   │   ├── Real-time Visualization    # 📈 Live Results
│   │   └── Debug Tools               # 🐛 Development Aid
│   │
│   ├── 📁 metrics/                    # 📈 Implementation Space
│   │   ├── 📄 __init__.py             # 📦 Module Marker
│   │   ├── 📄 metric_name.py          # 🔬 Your Metric Logic
│   │   ├── 📄 metric_name.yaml        # ⚙️ Configuration File
│   │   └── 📄 [more metrics...]       # 📊 Additional Metrics
│   │
│   └── 📁 scaffolding/                # 🛠️ Development Tools
│       ├── 📄 __init__.py             # 📦 Module Marker
│       └── 📄 cli.py                  # 💻 Command Interface
│           ├── create command         # ✨ Metric Generation
│           ├── Template System        # 📋 Pre-built Patterns
│           ├── dashboard command      # 📊 Testing Launch
│           ├── api command           # 🌐 Server Launch
│           └── list command          # 📝 Metric Listing
│
├── 📁 tests/                          # 🧪 Quality Assurance
│   ├── 📄 test_your_metric.py         # ✅ Generated Tests
│   ├── 📄 test_integration.py         # 🔗 System Tests
│   └── 📄 [more tests...]             # 🧪 Additional Tests
│
├── 📄 deploy_your_metric.py           # 🚀 Deployment Scripts
├── 📄 pyproject.toml                  # ⚙️ Package Config
├── 📄 requirements.txt                # 📋 Dependencies
└── 📄 README.md                       # 📖 Documentation
```

## 🎯 Three-Layer Architecture

### 🏗️ Layer 1: Metric Development

**Purpose**: Core metric calculation functions with rich outputs

```python
# 📍 Location: metrics_hub/metrics/your_metric.py
from metrics_hub import register_metric
import pandas as pd
import plotly.express as px

@register_metric("financial_analysis")
def calculate_financial_analysis(data_source: str, filters: dict = None):
    """Rich metric with multiple output types."""
    
    # 📊 DataFrame output
    analysis_df = perform_analysis(data_source, filters)
    
    # 📈 Interactive visualization  
    trend_chart = px.line(analysis_df, x='date', y='value')
    
    # 📋 Summary metrics
    summary = calculate_summary_stats(analysis_df)
    
    return {
        'analysis_table': analysis_df,     # 📊 Table format
        'trend_chart': trend_chart,        # 📈 Interactive chart  
        'summary_metrics': summary         # 📋 Key numbers
    }
```

**Configuration**: 
```yaml
# 📍 Location: metrics_hub/metrics/financial_analysis.yaml
id: financial_analysis
name: Financial Analysis
description: Comprehensive financial performance analysis
category: financial

inputs:
  - name: data_source
    type: string
    required: true
    description: Database connection or file path
    
  - name: filters
    type: object
    required: false
    description: Additional data filters

outputs:
  - name: analysis_table
    type: dataframe
    description: Analysis results table
    
  - name: trend_chart
    type: plotly_figure
    description: Interactive trend visualization
    
  - name: summary_metrics
    type: object
    description: Key performance indicators
```

### 🌐 Layer 2: API and Interfaces

**Purpose**: Expose metrics through multiple interfaces with rich output handling

```
🔗 API Endpoints (Auto-Generated)
├── GET  /metrics                     # 📋 List all available metrics
├── GET  /metrics/{metric_id}         # 📖 Get metric configuration
├── POST /calculate                   # 🎯 Calculate with JSON input
├── GET  /calculate/{metric_id}       # ⚡ Calculate with query params
├── GET  /calculate/{metric_id}/html  # 🌐 Rich HTML report
├── GET  /calculate/{metric_id}/csv   # 💾 CSV download (DataFrames)
└── GET  /health                      # 💚 Posit Connect health check
```

**Rich Output Processing**:
```python
# 🎨 Automatic format conversion
DataFrame → JSON (records) / HTML (table) / CSV (download)
Plotly    → JSON (spec) / HTML (embedded) / Interactive
Mixed     → JSON (typed) / HTML (report) / CSV (tables only)
```

**Example Responses**:
```bash
# 📊 JSON Response
GET /calculate/financial_analysis
{
  "analysis_table": [{"date": "2024-01", "value": 100}, ...],
  "trend_chart": {"data": [...], "layout": {...}},
  "summary_metrics": {"roi": 0.15, "risk": 0.08}
}

# 🌐 HTML Report  
GET /calculate/financial_analysis/html
<!DOCTYPE html>
<html>
  <head><script src="plotly.js"></script></head>
  <body>
    <h1>Financial Analysis</h1>
    <table class="table">...</table>
    <div id="chart">...</div>
  </body>
</html>

# 💾 CSV Download
GET /calculate/financial_analysis/csv
date,value,category
2024-01,100,revenue
2024-02,105,revenue
...
```

### 🛠️ Layer 3: Development Tools  

**Purpose**: Scaffolding, testing, and deployment tools

```bash
# 🎯 CLI Commands
metrics-hub create "Portfolio Analysis" \      # ✨ Generate metric
    --template dataframe \
    --category investment

metrics-hub dashboard                          # 📊 Launch testing UI
metrics-hub api --reload                       # 🌐 Launch API server  
metrics-hub list                              # 📋 Show all metrics
```

**Template System**:
```
🎨 Available Templates
├── 📊 simple       → Basic calculations
├── 📈 dataframe    → Data analysis & reporting  
├── 📉 plotly       → Interactive visualizations
└── 🔗 multi_source → Complex analytics with multiple data sources
```

**Generated Files**:
```
✨ For each metric creation:
├── 📄 metrics_hub/metrics/category_metric_name.py    # Implementation
├── 📄 metrics_hub/metrics/category_metric_name.yaml  # Configuration
├── 📄 tests/test_category_metric_name.py             # Test suite
└── 📄 deploy_category_metric_name.py                 # Posit deployment
```

## 🔄 Data Flow Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  📝 Developer   │    │  🏗️ Scaffolding │    │  📦 Package     │
│                 │───▶│                 │───▶│                 │
│ • Requirements  │    │ • CLI Generator │    │ • Metric Code   │
│ • Templates     │    │ • Templates     │    │ • YAML Config   │
│ • Categories    │    │ • Code Gen      │    │ • Tests         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ 🚀 Deployment  │    │  🌐 API/Dashboard│    │  🔧 Registry    │
│                 │◀───│                 │◀───│                 │
│ • Posit Connect │    │ • Multiple      │    │ • Auto-Discovery│
│ • Env Config    │    │   Formats       │    │ • Function Load │
│ • Health Checks │    │ • Rich Outputs  │    │ • Config Parse  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📊 Rich Output Support

### 🎨 Output Type Matrix

| Type | JSON API | HTML Report | CSV Download | Dashboard |
|------|----------|-------------|--------------|-----------|
| **DataFrame** | Records Array | Bootstrap Table | Direct Export | Interactive Table |
| **Plotly Figure** | Plot JSON | Embedded Chart | ❌ N/A | Interactive Chart |
| **Mixed Objects** | Type-Aware JSON | Full Report | Tables Only | Multi-Component |
| **Simple Values** | Direct Value | Styled Display | ❌ N/A | Gauge/KPI Card |

### 🔍 Processing Examples

```python
# 📊 DataFrame Processing
df = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})

# → JSON: [{"A": 1, "B": 3}, {"A": 2, "B": 4}]
# → HTML: <table class="table table-striped">...</table>  
# → CSV:  A,B\n1,3\n2,4

# 📈 Plotly Processing  
fig = px.scatter(df, x='A', y='B', title='Scatter Plot')

# → JSON: {"data": [...], "layout": {...}}
# → HTML: <div id="plot"><script>Plotly.newPlot(...)</script></div>
# → CSV:  ❌ Not applicable

# 🎯 Mixed Processing
result = {'data': df, 'chart': fig, 'kpi': 42}

# → JSON: {"data": [...], "chart": {...}, "kpi": 42}
# → HTML: Full report with table + embedded chart + KPI
# → CSV:  Only the DataFrame portion
```

## 🚀 Posit Connect Integration

### 🏗️ Deployment Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  📦 Metric      │    │  🌐 FastAPI     │    │  🚀 Posit       │
│     Package     │───▶│     App         │───▶│    Connect      │
│                 │    │                 │    │                 │
│ • Implementation│    │ • Rich Outputs  │    │ • Auto-Scale    │
│ • Configuration │    │ • Health Checks │    │ • Auth/Perms    │
│ • Dependencies  │    │ • Multi-Format  │    │ • Monitoring    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
                                              ┌─────────────────┐
                                              │  👥 End Users   │
                                              │                 │
                                              │ • HTML Reports  │
                                              │ • CSV Downloads │
                                              │ • JSON APIs     │
                                              │ • Interactive   │
                                              │   Charts        │
                                              └─────────────────┘
```

### 📜 Generated Deployment Script

```python
# 📄 deploy_your_metric.py (Auto-generated)
"""
Posit Connect deployment script for your_metric.
Auto-generated by Metrics Hub scaffolding system.
"""

import os
from metrics_hub.api import create_api_app

# 🔗 Import your metric to ensure registration
from metrics_hub.metrics.your_metric import calculate_your_metric

# 🌐 Create FastAPI app with all registered metrics
app = create_api_app()

# 🏠 Custom root endpoint for this deployment
@app.get("/", tags=["Metric Info"])
async def metric_info():
    """Get information about this specific metric deployment."""
    return {
        "metric_id": "your_metric",
        "function_name": "calculate_your_metric", 
        "status": "active",
        "endpoints": [
            "/metrics",                    # 📋 List all metrics
            "/calculate",                  # 🎯 JSON calculation
            "/calculate/your_metric/html", # 🌐 HTML report
            "/calculate/your_metric/csv",  # 💾 CSV download
            "/docs"                        # 📚 API documentation
        ],
        "description": "Metrics Hub deployment for your_metric"
    }

# 🔧 Local testing support
if __name__ == "__main__":
    import uvicorn
    
    # 🌍 Environment configuration
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    reload = os.environ.get("RELOAD", "false").lower() == "true"
    
    print(f"🚀 Starting your_metric deployment...")
    print(f"🌐 URL: http://{host}:{port}")
    print(f"📚 API Docs: http://{host}:{port}/docs")
    print(f"📊 HTML Report: http://{host}:{port}/calculate/your_metric/html")
    
    uvicorn.run("deploy_your_metric:app", host=host, port=port, reload=reload)
```

## 🔒 Security & Performance

### 🛡️ Security Features

```
🔐 Security Layers
├── 📝 Input Validation    → Pydantic models + YAML schemas
├── 🚫 SQL Injection      → Parameterized queries in templates  
├── 🔒 Data Privacy       → No sensitive data in logs
├── 🎫 Authentication     → Delegated to Posit Connect
└── 🚦 Rate Limiting      → FastAPI middleware support
```

### ⚡ Performance Optimizations

```
🏃 Performance Features
├── 🔄 Lazy Loading       → Metrics loaded on-demand
├── 📦 Format Caching     → Avoid redundant conversions
├── 🌊 Streaming          → Large DataFrames streamed as CSV
├── ⚡ Async Support      → Non-blocking API operations
└── 📊 Chunk Processing   → Handle large datasets efficiently
```

## 🎛️ Monitoring & Observability

### 📊 Built-in Monitoring

```
📈 Observability Stack
├── 💚 Health Checks      → /health endpoint for Posit Connect
├── 📝 Structured Logging → Configurable levels & formats
├── ⏱️ Execution Metrics  → Response times & success rates
├── 🚨 Error Handling     → Structured error responses
└── 📊 Usage Analytics    → Optional metric call tracking
```

### 🔍 Debug Tools

```bash
# 🐛 Development Debugging
metrics-hub dashboard --debug    # Verbose logging + error details
metrics-hub api --reload        # Hot reload + request logging

# 📊 Health Check Testing  
curl http://localhost:8000/health
{
  "status": "healthy",
  "service": "metrics-hub",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## 🔧 Extensibility Points

### 🎨 Adding New Output Types

```python
# 1️⃣ Update API processing (api.py)
elif isinstance(result, YourNewType):
    if output_format == "html":
        return "your_type", result.to_html()
    else:
        return "your_type", result.to_dict()

# 2️⃣ Update dashboard rendering (dashboard.py)  
elif isinstance(result, YourNewType):
    return html.Div([your_component_from_result(result)])

# 3️⃣ Update CLI templates (scaffolding/cli.py)
'your_new_type': 'YourNewType'
```

### 📋 Custom Templates

```python
# 1️⃣ Define template configuration
elif template_type == 'your_template':
    inputs = [...]
    outputs = [...]
    data_sources = [...]
    return inputs, outputs, data_sources

# 2️⃣ Update CLI choices
@click.option('--template', type=click.Choice([..., 'your_template']))
```

### 🔗 New Data Sources

```python
# 1️⃣ Add connection helpers
def _generate_your_source_connection(source_config):
    return f"# Connect to {source_config['name']}"

# 2️⃣ Update requirements
if 'your_source' in source_types:
    requirements.append('your-client-package>=1.0.0')
```

## 🛠️ Technology Stack

```
🏗️ Core Technologies
├── 🐍 Python 3.11+        → Modern Python features
├── 📊 pandas              → Data manipulation
├── 🔢 NumPy               → Numerical computing
├── 📈 Plotly              → Interactive visualizations
└── ⚙️ PyYAML              → Configuration management

🌐 Web Technologies  
├── 🚀 FastAPI             → Modern web framework
├── 🦄 Uvicorn             → ASGI server
├── 📝 Pydantic            → Data validation
└── 📊 Dash                → Interactive dashboards

🛠️ Development Tools
├── 💻 Click               → CLI framework
├── 🧪 pytest             → Testing framework
├── ⚡ pytest-asyncio      → Async testing
└── 🎯 Hatch              → Package building

🚀 Deployment
├── 📦 Posit Connect       → Primary deployment target
├── 🐳 Docker              → Containerization option
└── ☁️ Cloud platforms     → Kubernetes, Cloud Run, etc.
```

---

This architecture provides a **streamlined, developer-focused platform** for creating sophisticated metrics with rich outputs while maintaining **simplicity** and **deployment readiness** for Posit Connect environments.