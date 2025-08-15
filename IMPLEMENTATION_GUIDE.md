# Implementation Guide

## Overview

This guide provides technical implementation details for developers who want to understand the internals of Metrics Hub or extend its functionality.

## Project Structure

```
metrics-hub/
├── metrics_hub/                  # Main package
│   ├── __init__.py               # Package exports
│   ├── core.py                   # Metric registry and function management
│   ├── api.py                    # FastAPI interface with rich outputs
│   ├── dashboard.py              # Dash testing dashboard
│   ├── metrics/                  # Metric implementations
│   │   ├── __init__.py           # Metrics package
│   │   ├── example_metric.py     # Example metric implementation
│   │   └── example_metric.yaml   # Example metric configuration
│   └── scaffolding/              # CLI scaffolding tools
│       ├── __init__.py           # Scaffolding package
│       └── cli.py                # Command-line interface
├── tests/                        # Test suite
├── requirements.txt              # Dependencies
├── pyproject.toml               # Package configuration
├── README.md                    # Main documentation
├── USER_GUIDE.md                # User documentation
├── ARCHITECTURE.md              # Architecture overview
└── IMPLEMENTATION_GUIDE.md      # This file
```

## Core Components

### 1. Metric Registry (`core.py`)

The metric registry manages function registration and YAML configuration loading.

#### Key Classes

```python
class MetricRegistry:
    """Simple registry for metric functions."""
    
    def __init__(self, metrics_dir: str = "metrics"):
        self.metrics_dir = Path(metrics_dir)
        self.metrics: Dict[str, Dict[str, Any]] = {}  # YAML configs
        self._functions: Dict[str, Callable] = {}     # Python functions
    
    def load_metrics(self):
        """Load YAML configs and Python functions."""
        # Load YAML configurations
        for yaml_file in self.metrics_dir.glob("**/*.yaml"):
            config = yaml.safe_load(yaml_file.read_text())
            self.metrics[config['id']] = config
        
        # Load Python functions via dynamic import
        for py_file in self.metrics_dir.glob("**/*.py"):
            module = importlib.import_module(module_path)
            for name, obj in inspect.getmembers(module, inspect.isfunction):
                if hasattr(obj, '__metric_id__'):
                    self._functions[obj.__metric_id__] = obj
```

#### Registration Decorator

```python
def register_metric(metric_id: str):
    """Decorator to register a metric function."""
    def decorator(func: Callable):
        func.__metric_id__ = metric_id
        return func
    return decorator

# Usage
@register_metric("financial_analysis")
def calculate_financial_analysis(...):
    pass
```

#### Global Registry

```python
_registry = None

def get_registry() -> MetricRegistry:
    """Get or create global metric registry."""
    global _registry
    if _registry is None:
        _registry = MetricRegistry()
    return _registry
```

### 2. API Interface (`api.py`)

The FastAPI interface handles rich outputs including DataFrames and Plotly figures.

#### Rich Output Processing

```python
def _process_result(result: Any, output_format: str = "json") -> tuple[str, Any]:
    """Process result based on type and output format."""
    
    if isinstance(result, pd.DataFrame):
        if output_format == "csv":
            return "dataframe", result.to_csv(index=False)
        elif output_format == "html":
            return "dataframe", result.to_html(classes="table table-striped")
        else:
            return "dataframe", result.to_dict(orient="records")
    
    elif isinstance(result, (go.Figure, px._figure.Figure)):
        if output_format == "html":
            return "plotly", result.to_html(include_plotlyjs=True, full_html=True)
        else:
            return "plotly", result.to_dict()
    
    elif isinstance(result, dict):
        # Handle mixed outputs
        processed_dict = {}
        for key, value in result.items():
            if isinstance(value, pd.DataFrame):
                if output_format == "json":
                    processed_dict[key] = value.to_dict(orient="records")
                else:
                    processed_dict[key] = value.to_html(classes="table table-striped")
            # ... handle other types
        
        return "complex", processed_dict
```

#### Endpoint Patterns

```python
@app.post("/calculate")
async def calculate_metric(request: MetricRequest):
    """Calculate metric with rich output support."""
    result = registry.call_metric(request.metric_id, **request.inputs)
    result_type, processed_result = _process_result(result, request.output_format)
    
    return MetricResponse(
        metric_id=request.metric_id,
        result=processed_result,
        result_type=result_type,
        success=True,
        output_format=request.output_format
    )

@app.get("/calculate/{metric_id}/html")
async def calculate_metric_html(metric_id: str, **params):
    """Return full HTML report."""
    inputs = _convert_query_params(metric_id, params)
    result = registry.call_metric(metric_id, **inputs)
    html_content = _generate_html_output(metric_id, result, inputs)
    return HTMLResponse(content=html_content)

@app.get("/calculate/{metric_id}/csv")
async def calculate_metric_csv(metric_id: str, **params):
    """Return CSV download for DataFrames."""
    inputs = _convert_query_params(metric_id, params)
    result = registry.call_metric(metric_id, **inputs)
    
    if isinstance(result, pd.DataFrame):
        csv_content = result.to_csv(index=False)
        return Response(
            content=csv_content, 
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={metric_id}.csv"}
        )
```

#### HTML Report Generation

```python
def _generate_html_output(metric_id: str, result: Any, inputs: dict) -> str:
    """Generate comprehensive HTML output."""
    
    html_parts = [
        "<!DOCTYPE html>",
        "<html>",
        "<head>",
        f"<title>{metric_name} - Results</title>",
        "<script src='https://cdn.plot.ly/plotly-latest.min.js'></script>",
        "<link href='https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css' rel='stylesheet'>",
        "</head>",
        "<body>",
        f"<div class='container'><h1>{metric_name}</h1>",
    ]
    
    # Add inputs section
    html_parts.extend([
        "<h3>Inputs</h3>",
        "<table class='table table-sm'>",
        "<thead><tr><th>Parameter</th><th>Value</th></tr></thead>",
        "<tbody>"
    ])
    for key, value in inputs.items():
        html_parts.append(f"<tr><td>{key}</td><td>{str(value)}</td></tr>")
    html_parts.extend(["</tbody>", "</table>"])
    
    # Add results section
    if isinstance(result, pd.DataFrame):
        html_parts.append(result.to_html(classes="table table-striped"))
    elif isinstance(result, go.Figure):
        plot_div = result.to_html(include_plotlyjs=False, div_id="metric-plot")
        html_parts.append(plot_div)
    elif isinstance(result, dict):
        for key, value in result.items():
            html_parts.append(f"<h4>{key}</h4>")
            if isinstance(value, pd.DataFrame):
                html_parts.append(value.to_html(classes="table table-striped"))
            elif isinstance(value, go.Figure):
                plot_div = value.to_html(include_plotlyjs=False, div_id=f"plot-{key}")
                html_parts.append(plot_div)
    
    html_parts.extend(["</div>", "</body>", "</html>"])
    return "\\n".join(html_parts)
```

### 3. Dashboard Interface (`dashboard.py`)

The Dash dashboard provides interactive testing capabilities.

#### Dashboard Structure

```python
def create_dashboard_app() -> dash.Dash:
    """Create Dash application for metric testing."""
    
    app = dash.Dash(__name__, title="Metric Platform Dashboard")
    registry = get_registry()
    
    app.layout = html.Div([
        html.H1("Metric Platform Dashboard"),
        
        # Metric selection
        dcc.Dropdown(
            id="metric-dropdown",
            options=[
                {"label": f"{m.get('name', m['id'])} ({m['id']})", "value": m['id']}
                for m in registry.list_all()
            ],
        ),
        
        # Dynamic input controls (generated by callback)
        html.Div(id="input-controls"),
        
        # Calculate button
        html.Button("Calculate", id="calculate-btn"),
        
        # Results display
        html.Div(id="results-display"),
        html.Div(id="visualization")
    ])
```

#### Dynamic Form Generation

```python
@app.callback(
    [Output("input-controls", "children"), Output("calculate-btn", "disabled")],
    [Input("metric-dropdown", "value")]
)
def update_metric_selection(metric_id):
    if not metric_id:
        return "", True
    
    config = registry.get_config(metric_id)
    controls = []
    
    for input_param in config.get('inputs', []):
        param_name = input_param['name']
        param_type = input_param.get('type', 'string')
        
        if param_type in ['integer', 'float']:
            control = dcc.Input(
                id=f"input-{param_name}",
                type="number",
                placeholder=f"Enter {param_name}"
            )
        elif param_type == 'array':
            control = dcc.Textarea(
                id=f"input-{param_name}",
                placeholder="Enter comma-separated values"
            )
        else:
            control = dcc.Input(
                id=f"input-{param_name}",
                type="text",
                placeholder=f"Enter {param_name}"
            )
        
        controls.append(html.Div([
            html.Label(param_name),
            control
        ]))
    
    return controls, False
```

#### Visualization Rendering

```python
def create_visualization(result: Any, config: Dict[str, Any]) -> html.Div:
    """Create visualization based on result type."""
    
    if isinstance(result, (int, float)):
        # Gauge chart for single values
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=result,
            title={'text': config.get('name', 'Metric Value')}
        ))
        return html.Div([dcc.Graph(figure=fig)])
    
    elif isinstance(result, pd.DataFrame):
        # Data table for DataFrames
        return html.Div([
            dash_table.DataTable(
                data=result.to_dict('records'),
                columns=[{"name": i, "id": i} for i in result.columns],
                page_size=10,
                sort_action="native",
                filter_action="native"
            )
        ])
    
    elif isinstance(result, go.Figure):
        # Direct Plotly figure
        return html.Div([dcc.Graph(figure=result)])
    
    elif isinstance(result, dict):
        # Mixed results
        components = []
        for key, value in result.items():
            components.append(html.H4(key))
            if isinstance(value, pd.DataFrame):
                components.append(dash_table.DataTable(
                    data=value.to_dict('records'),
                    columns=[{"name": i, "id": i} for i in value.columns]
                ))
            elif isinstance(value, go.Figure):
                components.append(dcc.Graph(figure=value))
        
        return html.Div(components)
```

### 4. CLI Generator (`cli.py`)

The CLI generates complete metric packages with templates.

#### Template System

```python
def _get_template_config(template_type: str):
    """Get predefined template configurations."""
    
    if template_type == 'dataframe':
        inputs = [
            {'name': 'data_source', 'type': 'database_connection', 'required': True},
            {'name': 'query', 'type': 'string', 'required': True},
            {'name': 'filters', 'type': 'object', 'required': False}
        ]
        outputs = [
            {'name': 'result_table', 'type': 'dataframe'},
            {'name': 'summary_stats', 'type': 'object'}
        ]
        data_sources = [
            {'name': 'primary_db', 'type': 'database', 'connection': 'postgresql://...'}
        ]
    
    elif template_type == 'plotly':
        inputs = [
            {'name': 'data', 'type': 'dataframe', 'required': True},
            {'name': 'chart_type', 'type': 'string', 'default': 'line'},
            {'name': 'title', 'type': 'string', 'required': False}
        ]
        outputs = [
            {'name': 'chart', 'type': 'plotly_figure'},
            {'name': 'data_table', 'type': 'plotly_table'}
        ]
        data_sources = []
    
    return inputs, outputs, data_sources
```

#### Code Generation

```python
def _generate_complex_python_code(metric_id, function_name, name, description, 
                                inputs, outputs, data_sources):
    """Generate Python code template with rich outputs."""
    
    # Dynamic imports based on outputs and data sources
    imports = ['import pandas as pd', 'import numpy as np']
    
    output_types = [out.get('type', '') for out in outputs]
    if any('plotly' in ot for ot in output_types):
        imports.extend(['import plotly.graph_objects as go', 'import plotly.express as px'])
    
    source_types = [ds.get('type', '') for ds in data_sources]
    if 'database' in source_types:
        imports.append('import sqlalchemy as sa')
    
    # Generate function signature with proper type hints
    params = []
    for inp in inputs:
        param_type = _get_python_type_hint(inp['type'])
        if inp['required']:
            params.append(f"{inp['name']}: {param_type}")
        else:
            default_val = inp.get('default', 'None')
            params.append(f"{inp['name']}: {param_type} = {default_val}")
    
    # Generate return type
    if len(outputs) == 1:
        return_type = _get_python_type_hint(outputs[0]['type'])
    else:
        return_type = "Dict[str, Union[pd.DataFrame, go.Figure, Any]]"
    
    # Template assembly
    return f'''"""
{description}
"""

{chr(10).join(imports)}
from metric_platform import register_metric
import logging

logger = logging.getLogger(__name__)

@register_metric("{metric_id}")
def {function_name}({', '.join(params)}) -> {return_type}:
    """
    {description}
    """
    try:
        # Input validation
        {_generate_validation_code(inputs)}
        
        # Data source connections
        {_generate_data_connections(data_sources)}
        
        # Main calculation logic
        {_generate_calculation_logic(outputs)}
        
    except Exception as e:
        logger.error(f"Calculation failed: {{e}}")
        raise RuntimeError(f"Metric calculation failed: {{e}}") from e
'''
```

#### Posit Connect Deployment

```python
def _generate_posit_deploy_script(metric_id: str, function_name: str) -> str:
    """Generate Posit Connect deployment script."""
    
    return f'''"""
Posit Connect deployment script for {metric_id}.
"""

import os
from metric_platform.api import create_api_app
from {metric_id} import {function_name}

# Create the FastAPI app
app = create_api_app()

# Add custom endpoint for this specific metric
@app.get("/")
async def root():
    return {{
        "metric_id": "{metric_id}",
        "status": "active",
        "endpoints": [
            "/calculate/{metric_id}",
            "/calculate/{metric_id}/html",
            "/calculate/{metric_id}/csv"
        ]
    }}

# For Posit Connect deployment
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    import uvicorn
    uvicorn.run("deploy_{metric_id}:app", host=host, port=port, reload=False)
'''
```

## Extension Points

### Adding New Output Types

1. **Update API processing**:
```python
# In api.py _process_result()
elif isinstance(result, YourNewType):
    if output_format == "html":
        return "your_type", result.to_html()
    else:
        return "your_type", result.to_dict()
```

2. **Update dashboard rendering**:
```python
# In dashboard.py create_visualization()
elif isinstance(result, YourNewType):
    return html.Div([your_component_from_result(result)])
```

3. **Update CLI templates**:
```python
# In cli.py _get_python_type_hint()
'your_new_type': 'YourNewType'
```

### Adding New Templates

1. **Define template configuration**:
```python
# In cli.py _get_template_config()
elif template_type == 'your_template':
    inputs = [...]
    outputs = [...]
    data_sources = [...]
    return inputs, outputs, data_sources
```

2. **Update CLI choices**:
```python
@click.option('--template', type=click.Choice([..., 'your_template']))
```

### Custom Data Sources

1. **Add connection helpers**:
```python
def _generate_your_source_connection(source_config):
    return f"# Connect to {source_config['name']}\\n# your_client = YourClient('{source_config['connection']}')"
```

2. **Update requirements generation**:
```python
# In cli.py _get_requirements()
if 'your_source' in source_types:
    requirements.append('your-client-package>=1.0.0')
```

## Testing Strategy

### Unit Tests

```python
# tests/test_metrics.py
def test_metric_registry():
    registry = MetricRegistry('test_metrics')
    assert len(registry.list_all()) > 0

def test_metric_calculation():
    result = call_metric('test_metric', data=[1, 2, 3])
    assert result is not None

# tests/test_api.py  
def test_api_endpoints():
    with TestClient(app) as client:
        response = client.get("/metrics")
        assert response.status_code == 200
        
        response = client.post("/calculate", json={
            "metric_id": "test_metric",
            "inputs": {"data": [1, 2, 3]}
        })
        assert response.status_code == 200
```

### Integration Tests

```python
# tests/test_integration.py
def test_full_workflow():
    # Create metric
    subprocess.run(['metric-platform', 'create', 'test_metric', '--category', 'test'])
    
    # Test API
    with TestClient(create_api_app()) as client:
        response = client.get("/calculate/test_metric/html")
        assert response.status_code == 200
```

## Performance Considerations

### Memory Management

```python
# For large DataFrames
def process_large_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    if len(df) > 100000:
        # Sample or chunk processing
        return df.sample(n=10000)
    return df
```

### Caching

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_calculation(params_hash: str) -> Any:
    # Expensive operation
    pass
```

### Async Operations

```python
import asyncio
import aiohttp

async def fetch_external_data(urls: List[str]) -> List[Dict]:
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url(session, url) for url in urls]
        return await asyncio.gather(*tasks)
```

## Security Considerations

### Input Validation

```python
def validate_sql_query(query: str) -> bool:
    """Basic SQL injection prevention."""
    dangerous_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'CREATE', 'ALTER']
    return not any(keyword in query.upper() for keyword in dangerous_keywords)
```

### Data Privacy

```python
def sanitize_output(data: pd.DataFrame, sensitive_columns: List[str]) -> pd.DataFrame:
    """Remove or mask sensitive data."""
    result = data.copy()
    for col in sensitive_columns:
        if col in result.columns:
            result[col] = '***REDACTED***'
    return result
```

This implementation guide provides the technical foundation for understanding and extending the Metric Platform. The modular design allows for easy customization while maintaining the core functionality for rich output handling and Posit Connect deployment.