# Metrics Hub User Guide

A comprehensive guide for developing, testing, and deploying complex metrics with rich outputs using Metrics Hub.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Creating Your First Metric](#creating-your-first-metric)
3. [Working with Templates](#working-with-templates)
4. [Rich Output Types](#rich-output-types)
5. [Testing and Development](#testing-and-development)
6. [Deployment to Posit Connect](#deployment-to-posit-connect)
7. [Advanced Usage](#advanced-usage)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)

## Getting Started

### Installation

```bash
# Basic installation
pip install metrics-hub

# With all features (recommended)
pip install "metrics-hub[all]"

# Or install specific features
pip install "metrics-hub[dashboard,database]"
```

### Verify Installation

```bash
metrics-hub --help
```

### Project Setup

## Creating Your First Metric

### Quick Start with Templates

```bash
# Create a simple DataFrame-based metric
metrics-hub create "Sales Analysis" \
    --category performance \
    --description "Monthly sales performance analysis" \
    --template dataframe

# Create an interactive visualization metric  
metrics-hub create "Trend Visualization" \
    --category operational \
    --description "Interactive trend charts" \
    --template plotly

# Create a complex multi-source metric
metrics-hub create "Portfolio Risk Analysis" \
    --category financial \
    --description "Comprehensive risk analysis with multiple data sources" \
    --template multi_source
```

### Interactive Creation

For full control over your metric definition:

```bash
metric-platform create "Custom Analysis" \
    --category custom \
    --description "Custom business analysis" \
    --complex \
    --interactive
```

This will prompt you to define:
- Input parameters and their types
- Output formats (DataFrames, Plotly charts, etc.)
- Data sources (databases, APIs, files)

### Generated Files

Each metric creation generates a complete package:

```
metrics/
├── category_metric_name.py              # Implementation
├── category_metric_name.yaml            # Configuration  
├── test_category_metric_name.py         # Test suite
├── deploy_category_metric_name.py       # Posit Connect deployment
└── category_metric_name_requirements.txt # Dependencies
```

## Working with Templates

### DataFrame Template

Perfect for data analysis and reporting:

```python
@register_metric("performance_sales_analysis")
def calculate_sales_analysis(
    data_source: str,
    query: str,
    filters: Dict[str, Any] = None
) -> Dict[str, Union[pd.DataFrame, Dict[str, Any]]]:
    """Monthly sales performance analysis."""
    
    # Connect to database
    engine = sa.create_engine(data_source)
    
    # Execute query
    df = pd.read_sql(query, engine)
    
    # Apply filters
    if filters:
        for column, value in filters.items():
            df = df[df[column] == value]
    
    # Calculate summary statistics
    summary = {
        'total_sales': df['sales'].sum(),
        'avg_sales': df['sales'].mean(),
        'top_product': df.groupby('product')['sales'].sum().idxmax()
    }
    
    return {
        'result_table': df,
        'summary_stats': summary
    }
```

### Plotly Template

For interactive visualizations:

```python
@register_metric("operational_trend_visualization") 
def calculate_trend_visualization(
    data: pd.DataFrame,
    chart_type: str = 'line',
    title: str = None
) -> Dict[str, go.Figure]:
    """Interactive trend charts."""
    
    # Create main chart
    if chart_type == 'line':
        fig = px.line(data, x='date', y='value', title=title)
    elif chart_type == 'bar':
        fig = px.bar(data, x='date', y='value', title=title)
    else:
        fig = px.scatter(data, x='date', y='value', title=title)
    
    # Create data table
    table_fig = go.Figure(data=[go.Table(
        header=dict(values=list(data.columns)),
        cells=dict(values=[data[col] for col in data.columns])
    )])
    
    return {
        'chart': fig,
        'data_table': table_fig
    }
```

### Multi-Source Template

For comprehensive analytics:

```python
@register_metric("financial_portfolio_risk_analysis")
def calculate_portfolio_risk_analysis(
    analysis_config: Dict[str, Any],
    date_range: Dict[str, Any],
    filters: Dict[str, Any] = None
) -> Dict[str, Union[pd.DataFrame, go.Figure, Dict[str, Any]]]:
    """Comprehensive portfolio risk analysis."""
    
    # Load data from multiple sources
    portfolio_data = _load_portfolio_data(analysis_config['portfolio_db'])
    market_data = _load_market_data(analysis_config['market_api'])
    reference_data = _load_reference_data(analysis_config['reference_files'])
    
    # Perform analysis
    risk_analysis = _calculate_portfolio_risk(
        portfolio_data, market_data, reference_data, date_range
    )
    
    # Create visualizations
    trend_chart = _create_risk_trend_chart(risk_analysis)
    
    # Calculate key metrics
    key_metrics = {
        'var_95': risk_analysis['var_95'].iloc[-1],
        'max_drawdown': risk_analysis['drawdown'].min(),
        'sharpe_ratio': _calculate_sharpe_ratio(risk_analysis)
    }
    
    return {
        'analysis_report': risk_analysis,
        'trend_chart': trend_chart,
        'summary_metrics': key_metrics
    }
```

## Rich Output Types

### DataFrames

Return pandas DataFrames for tabular data:

```python
# Simple DataFrame
return pd.DataFrame({
    'Portfolio': ['A', 'B', 'C'],
    'Return': [0.12, 0.08, 0.15],
    'Risk': [0.18, 0.12, 0.22]
})

# Complex DataFrame with multi-index
df = pd.DataFrame(data)
df.set_index(['Date', 'Portfolio'], inplace=True)
return df
```

**Output Formats:**
- **JSON API**: `{"Portfolio": ["A", "B", "C"], ...}`
- **HTML**: Bootstrap-styled table
- **CSV**: Direct download via `/csv` endpoint

### Plotly Figures

Return interactive visualizations:

```python
import plotly.graph_objects as go
import plotly.express as px

# Line chart
fig = go.Figure()
fig.add_trace(go.Scatter(x=dates, y=values, name='Trend'))
fig.update_layout(title='Performance Trend')

# Express charts (recommended)
fig = px.line(df, x='date', y='value', color='category', title='Multi-Series Trend')

# Statistical plots
fig = px.box(df, x='category', y='value', title='Distribution Analysis')

return fig
```

**Output Formats:**
- **JSON API**: Plotly JSON specification
- **HTML**: Embedded interactive chart with Plotly.js
- **Dashboard**: Full interactivity with zoom/pan

### Mixed Objects

Return complex combinations:

```python
return {
    'main_analysis': pd.DataFrame(...),      # Tabular data
    'trend_chart': go.Figure(...),           # Interactive chart
    'risk_metrics': {                        # Summary statistics
        'var_95': 0.045,
        'sharpe_ratio': 1.2
    },
    'correlation_matrix': correlation_df,    # Another DataFrame
    'distribution_plot': px.histogram(...)   # Another chart
}
```

### Advanced Plotly Examples

```python
# Subplots
from plotly.subplots import make_subplots

fig = make_subplots(rows=2, cols=1, subplot_titles=['Returns', 'Risk'])
fig.add_trace(go.Scatter(x=dates, y=returns), row=1, col=1)
fig.add_trace(go.Scatter(x=dates, y=risk), row=2, col=1)

# 3D plots
fig = go.Figure(data=[go.Scatter3d(
    x=df['x'], y=df['y'], z=df['z'],
    mode='markers',
    marker=dict(size=5, color=df['color'])
)])

# Financial charts
fig = go.Figure(data=[go.Candlestick(
    x=df['date'],
    open=df['open'], high=df['high'],
    low=df['low'], close=df['close']
)])

return fig
```

## Testing and Development

### Local Testing

```bash
# Run tests for a specific metric
pytest test_financial_portfolio_risk_analysis.py -v

# Run all metric tests
pytest metrics/ -v

# Run with coverage
pytest --cov=metrics --cov-report=html
```

### Interactive Dashboard

Launch the development dashboard:

```bash
metric-platform dashboard
```

Visit `http://localhost:8050` to:
- Select and test metrics interactively
- Provide inputs through auto-generated forms  
- View rich outputs (tables, charts, mixed)
- Export results as CSV or HTML
- Debug calculation issues

### API Testing

Launch the API server:

```bash
metric-platform api --reload
```

Test endpoints:

```bash
# List available metrics
curl http://localhost:8000/metrics

# Get metric info
curl http://localhost:8000/metrics/financial_portfolio_risk_analysis

# Calculate metric (JSON)
curl -X POST http://localhost:8000/calculate \
     -H "Content-Type: application/json" \
     -d '{"metric_id": "financial_portfolio_risk_analysis", "inputs": {...}}'

# Get HTML report
curl "http://localhost:8000/calculate/financial_portfolio_risk_analysis/html?param1=value1"

# Download CSV
curl "http://localhost:8000/calculate/financial_portfolio_risk_analysis/csv?param1=value1"
```

### Manual Testing

```python
# Test your metric directly
from metrics.financial_portfolio_risk_analysis import calculate_portfolio_risk_analysis

result = calculate_portfolio_risk_analysis(
    analysis_config={'portfolio_db': 'postgresql://...'},
    date_range={'start': '2024-01-01', 'end': '2024-12-31'}
)

print(type(result))
if isinstance(result, dict):
    for key, value in result.items():
        print(f"{key}: {type(value)}")
```

## Deployment to Posit Connect

### Prerequisites

1. Posit Connect server access
2. `rsconnect-python` installed:
   ```bash
   pip install rsconnect-python
   ```

### Local Testing

First, test your deployment script locally:

```bash
python deploy_financial_portfolio_risk_analysis.py
```

This starts a local server identical to what will run on Posit Connect.

### Deploy to Posit Connect

```bash
# Configure rsconnect (first time only)
rsconnect add --account myaccount --name myserver --url https://my-posit-connect.com --api-key my-api-key

# Deploy the metric
rsconnect deploy fastapi deploy_financial_portfolio_risk_analysis.py \
    --account myaccount \
    --title "Portfolio Risk Analysis" \
    --python /path/to/python
```

### Verify Deployment

Your deployed metric will be available at:
- `https://my-posit-connect.com/content/your-app-id/` - Main interface
- `https://my-posit-connect.com/content/your-app-id/calculate/your-metric-id/html` - HTML report
- `https://my-posit-connect.com/content/your-app-id/docs` - API documentation

### Environment Variables

Configure environment-specific settings:

```python
# In your deployment script
import os

# Database connections
DB_URL = os.environ.get('DATABASE_URL', 'postgresql://localhost/default')

# API keys
API_KEY = os.environ.get('EXTERNAL_API_KEY')

# Feature flags
ENABLE_CACHE = os.environ.get('ENABLE_CACHE', 'true').lower() == 'true'
```

## Advanced Usage

### Custom Data Sources

Add database connectivity:

```python
import sqlalchemy as sa
import pandas as pd

def load_portfolio_data(connection_string: str, date_range: Dict[str, Any]) -> pd.DataFrame:
    """Load portfolio data from database."""
    engine = sa.create_engine(connection_string)
    
    query = """
    SELECT portfolio_id, date, value, return_rate
    FROM portfolio_returns 
    WHERE date BETWEEN %(start_date)s AND %(end_date)s
    """
    
    return pd.read_sql(query, engine, params=date_range)
```

Add API connectivity:

```python
import requests
import pandas as pd

def load_market_data(api_endpoint: str, symbols: List[str]) -> pd.DataFrame:
    """Load market data from external API."""
    headers = {'Authorization': f'Bearer {API_KEY}'}
    
    data = []
    for symbol in symbols:
        response = requests.get(f"{api_endpoint}/quotes/{symbol}", headers=headers)
        response.raise_for_status()
        data.append(response.json())
    
    return pd.DataFrame(data)
```

### Error Handling

Add robust error handling:

```python
@register_metric("robust_analysis")
def calculate_robust_analysis(data_config: Dict[str, Any]) -> Dict[str, Any]:
    """Analysis with comprehensive error handling."""
    try:
        # Validate inputs
        if not data_config:
            raise ValueError("data_config is required")
        
        # Load and validate data
        df = load_data(data_config)
        if df.empty:
            raise ValueError("No data found for given parameters")
        
        # Perform calculations
        result = complex_calculation(df)
        
        # Validate outputs
        if result is None:
            raise RuntimeError("Calculation failed to produce results")
        
        return result
        
    except ValueError as e:
        logger.error(f"Input validation failed: {e}")
        raise
    except ConnectionError as e:
        logger.error(f"Data source connection failed: {e}")
        raise RuntimeError(f"Unable to connect to data source: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in calculation: {e}")
        raise RuntimeError(f"Calculation failed: {e}")
```

### Performance Optimization

For large datasets:

```python
import dask.dataframe as dd

@register_metric("large_dataset_analysis")
def calculate_large_dataset_analysis(query_config: Dict[str, Any]) -> pd.DataFrame:
    """Handle large datasets efficiently."""
    
    # Use Dask for large datasets
    ddf = dd.read_sql_table('large_table', connection_string, index_col='id')
    
    # Perform computations
    result = ddf.groupby('category').value.mean().compute()
    
    # Return manageable DataFrame
    return result.head(1000)  # Limit output size
```

For streaming results:

```python
@register_metric("streaming_analysis") 
def calculate_streaming_analysis(config: Dict[str, Any]) -> pd.DataFrame:
    """Stream large results efficiently."""
    
    # Use chunked processing
    chunks = []
    for chunk in pd.read_sql(query, engine, chunksize=10000):
        processed_chunk = process_chunk(chunk)
        chunks.append(processed_chunk)
    
    return pd.concat(chunks, ignore_index=True)
```

## Best Practices

### Code Organization

```python
# metric_helpers.py - Shared utilities
def validate_date_range(start_date: str, end_date: str) -> bool:
    """Validate date range inputs."""
    pass

def load_reference_data(file_path: str) -> pd.DataFrame:
    """Load reference data from file."""
    pass

# your_metric.py - Main metric
from .metric_helpers import validate_date_range, load_reference_data

@register_metric("well_organized_metric")
def calculate_well_organized_metric(...):
    """Well-organized metric with helper functions."""
    pass
```

### Configuration Management

```yaml
# config.yaml - External configuration
database:
  host: localhost
  port: 5432
  name: analytics_db
  
api:
  endpoint: https://api.example.com
  timeout: 30
  
calculations:
  window_size: 30
  confidence_level: 0.95
```

```python
# Load configuration
import yaml

with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

@register_metric("configurable_metric")
def calculate_configurable_metric(user_inputs: Dict[str, Any]) -> Any:
    """Use external configuration."""
    
    # Merge user inputs with defaults
    full_config = {**config['calculations'], **user_inputs}
    
    # Use configuration
    window = full_config['window_size']
    confidence = full_config['confidence_level']
```

### Testing Strategies

```python
# test_your_metric.py
import pytest
import pandas as pd
from unittest.mock import patch, Mock

class TestYourMetric:
    
    @pytest.fixture
    def sample_data(self):
        """Provide consistent test data."""
        return pd.DataFrame({
            'date': pd.date_range('2024-01-01', periods=100),
            'value': np.random.randn(100)
        })
    
    def test_basic_calculation(self, sample_data):
        """Test with valid inputs."""
        result = calculate_your_metric(sample_data)
        assert isinstance(result, dict)
        assert 'main_output' in result
    
    @patch('your_metric.load_external_data')
    def test_with_mocked_data(self, mock_load, sample_data):
        """Test with mocked external dependencies."""
        mock_load.return_value = sample_data
        
        result = calculate_your_metric({'source': 'external'})
        assert result is not None
        mock_load.assert_called_once()
    
    def test_error_conditions(self):
        """Test error handling."""
        with pytest.raises(ValueError, match="Invalid input"):
            calculate_your_metric(None)
```

### Documentation

```python
@register_metric("well_documented_metric")
def calculate_well_documented_metric(
    data_source: str,
    analysis_params: Dict[str, Any],
    optional_filters: Dict[str, Any] = None
) -> Dict[str, Union[pd.DataFrame, go.Figure]]:
    """
    Calculate comprehensive business analysis with multiple outputs.
    
    This metric performs advanced analytics combining multiple data sources
    to produce rich visualizations and detailed reports.
    
    Args:
        data_source (str): Database connection string or file path
        analysis_params (Dict[str, Any]): Configuration for analysis including:
            - date_range: {'start': 'YYYY-MM-DD', 'end': 'YYYY-MM-DD'}
            - metrics: List of metrics to calculate
            - granularity: 'daily', 'weekly', or 'monthly'
        optional_filters (Dict[str, Any], optional): Additional filters:
            - region: Filter by geographical region
            - product_category: Filter by product category
    
    Returns:
        Dict[str, Union[pd.DataFrame, go.Figure]]: Results containing:
            - analysis_table: Main results as DataFrame
            - trend_chart: Interactive Plotly visualization
            - summary_stats: Key performance indicators
    
    Raises:
        ValueError: If required parameters are missing or invalid
        ConnectionError: If unable to connect to data source
        RuntimeError: If calculation fails
    
    Example:
        >>> result = calculate_well_documented_metric(
        ...     data_source="postgresql://user:pass@host/db",
        ...     analysis_params={
        ...         'date_range': {'start': '2024-01-01', 'end': '2024-12-31'},
        ...         'metrics': ['revenue', 'profit', 'customers'],
        ...         'granularity': 'monthly'
        ...     }
        ... )
        >>> print(result['analysis_table'].shape)
        (12, 4)
    """
    # Implementation here
    pass
```

## Troubleshooting

### Common Issues

#### 1. Import Errors

```bash
# Error: ModuleNotFoundError: No module named 'your_metric'
# Solution: Ensure metric is in Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or add to metric file:
import sys
sys.path.append('.')
```

#### 2. Database Connection Issues

```python
# Error: Could not connect to database
# Solution: Test connection separately
import sqlalchemy as sa

try:
    engine = sa.create_engine(connection_string)
    with engine.connect() as conn:
        result = conn.execute(sa.text("SELECT 1"))
        print("Connection successful")
except Exception as e:
    print(f"Connection failed: {e}")
```

#### 3. Plotly Rendering Issues

```python
# Error: Plotly charts not displaying
# Solution: Ensure proper figure creation
import plotly.graph_objects as go

# ❌ Incorrect
fig = go.Figure
return fig

# ✅ Correct  
fig = go.Figure()
fig.add_trace(go.Scatter(x=[1,2,3], y=[1,2,3]))
return fig
```

#### 4. Large Dataset Memory Issues

```python
# Error: Memory error with large DataFrames
# Solution: Use chunking or sampling
def process_large_dataset(query: str) -> pd.DataFrame:
    chunks = []
    for chunk in pd.read_sql(query, engine, chunksize=10000):
        # Process chunk
        processed = chunk.groupby('category').sum()
        chunks.append(processed)
    
    return pd.concat(chunks)
```

### Debugging Tips

1. **Enable Verbose Logging**:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **Test Individual Components**:
   ```python
   # Test data loading separately
   data = load_data(config)
   print(f"Loaded {len(data)} rows")
   
   # Test calculation separately  
   result = calculate_metrics(data)
   print(f"Result type: {type(result)}")
   ```

3. **Use Dashboard for Interactive Debugging**:
   ```bash
   metric-platform dashboard --debug
   ```

4. **Check API Responses**:
   ```bash
   # Test with curl
   curl -v http://localhost:8000/calculate/your_metric_id/html
   ```

### Performance Monitoring

```python
import time
from functools import wraps

def timing_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end - start:.2f} seconds")
        return result
    return wrapper

@timing_decorator
@register_metric("monitored_metric")
def calculate_monitored_metric(...):
    """Metric with performance monitoring."""
    pass
```

### Getting Help

1. **Check Logs**: Look for error messages in the console output
2. **Validate YAML**: Ensure metric configuration is valid YAML
3. **Test Dependencies**: Verify all required packages are installed
4. **Use Templates**: Start with working templates and modify incrementally
5. **Community Support**: Check GitHub issues for similar problems

This comprehensive guide should help you develop sophisticated metrics efficiently using the Metric Platform. Remember to start simple and add complexity gradually as you become more familiar with the system.