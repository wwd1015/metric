"""
Command-line interface for generating metrics within the package.

Provides scaffolding tools to create metric templates with YAML configurations,
test files, and deployment scripts that work within the metrics-hub package structure.
"""

import click
import yaml
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


@click.group()
def cli():
    """Metrics Hub - CLI for metric scaffolding and deployment."""
    pass


@cli.command()
@click.argument('name')
@click.option('--category', default='general', help='Metric category')
@click.option('--description', default='', help='Metric description')
@click.option('--template', type=click.Choice(['simple', 'dataframe', 'plotly', 'multi_source']), 
              default='simple', help='Template type')
@click.option('--complex', is_flag=True, help='Create complex metric with multiple outputs')
@click.option('--interactive', is_flag=True, help='Interactive parameter definition')
def create(name: str, category: str, description: str, template: str, complex: bool, interactive: bool):
    """Create a new metric within the metrics-hub package."""
    
    # Clean and format names
    metric_id = _clean_metric_id(name, category)
    function_name = _create_function_name(name)
    
    click.echo(f"Creating metric: {metric_id}")
    click.echo(f"Template: {template}")
    click.echo(f"Category: {category}")
    
    # Get or generate configuration
    if interactive:
        inputs, outputs, data_sources = _interactive_config()
    else:
        inputs, outputs, data_sources = _get_template_config(template)
    
    # Generate files within the package structure
    _generate_metric_files(
        metric_id=metric_id,
        function_name=function_name,
        name=name,
        category=category,
        description=description,
        template=template,
        inputs=inputs,
        outputs=outputs,
        data_sources=data_sources,
        complex=complex
    )
    
    click.echo(f"✅ Created metric '{metric_id}' in metrics_hub/metrics/")
    click.echo(f"📁 Files created:")
    click.echo(f"   - metrics_hub/metrics/{metric_id}.py")
    click.echo(f"   - metrics_hub/metrics/{metric_id}.yaml")
    click.echo(f"   - tests/test_{metric_id}.py")
    click.echo(f"   - deploy_{metric_id}.py")
    
    click.echo("\n🚀 Next steps:")
    click.echo(f"   1. Implement the metric logic in metrics_hub/metrics/{metric_id}.py")
    click.echo(f"   2. Test with: python -m pytest tests/test_{metric_id}.py")
    click.echo(f"   3. Test interactively: metrics-hub dashboard")
    click.echo(f"   4. Deploy to Posit Connect: python deploy_{metric_id}.py")


@cli.command()
@click.option('--host', default='127.0.0.1', help='Host to bind to')
@click.option('--port', default=8050, help='Port to bind to')
@click.option('--debug', is_flag=True, help='Enable debug mode')
def dashboard(host: str, port: int, debug: bool):
    """Launch the interactive dashboard for testing metrics."""
    from ..dashboard import run_dashboard
    
    click.echo(f"Starting Metrics Hub Dashboard...")
    click.echo(f"URL: http://{host}:{port}")
    
    try:
        run_dashboard(host=host, port=port, debug=debug)
    except KeyboardInterrupt:
        click.echo("\nShutting down dashboard...")
    except ImportError as e:
        click.echo(f"❌ Dashboard dependencies not installed: {e}")
        click.echo("Install with: pip install 'metrics-hub[dashboard]'")


@cli.command()
@click.option('--host', default='0.0.0.0', help='Host to bind to')
@click.option('--port', default=8000, help='Port to bind to')
@click.option('--reload', is_flag=True, help='Enable auto-reload')
def api(host: str, port: int, reload: bool):
    """Launch the API server for metric calculation."""
    from ..api import run_api_server
    
    click.echo(f"Starting Metrics Hub API...")
    click.echo(f"URL: http://{host}:{port}")
    click.echo(f"Docs: http://{host}:{port}/docs")
    
    try:
        run_api_server(host=host, port=port, reload=reload)
    except KeyboardInterrupt:
        click.echo("\nShutting down API server...")
    except ImportError as e:
        click.echo(f"❌ API dependencies not installed: {e}")
        click.echo("Install with: pip install 'metrics-hub[api]'")


@cli.command()
def list():
    """List all available metrics in the package."""
    from ..core import get_registry
    
    try:
        registry = get_registry()
        metrics = registry.list_all()
        
        if not metrics:
            click.echo("No metrics found in the package.")
            return
        
        click.echo(f"Found {len(metrics)} metrics:\n")
        for metric in metrics:
            click.echo(f"📊 {metric['id']}")
            click.echo(f"   Name: {metric.get('name', 'N/A')}")
            click.echo(f"   Category: {metric.get('category', 'N/A')}")
            click.echo(f"   Description: {metric.get('description', 'N/A')}")
            
            inputs = metric.get('inputs', [])
            if inputs:
                click.echo(f"   Inputs: {', '.join([inp['name'] for inp in inputs])}")
            click.echo()
            
    except Exception as e:
        click.echo(f"❌ Failed to list metrics: {e}")


@cli.command()
@click.argument('metric_id')
@click.option('--force', is_flag=True, help='Skip confirmation prompt')
def remove(metric_id: str, force: bool):
    """Remove a metric and all its related files."""
    import os
    from pathlib import Path
    
    click.echo(f"🗑️  Removing metric: {metric_id}")
    
    # Check if metric exists first
    from ..core import get_registry
    try:
        registry = get_registry()
        config = registry.get_config(metric_id)
        if not config:
            click.echo(f"❌ Metric '{metric_id}' not found.")
            click.echo("Use 'metrics-hub list' to see available metrics.")
            return
    except Exception as e:
        click.echo(f"⚠️  Could not verify metric existence: {e}")
    
    # List files that will be removed
    files_to_remove = []
    
    # 1. Python implementation file
    python_file = Path(f"metrics_hub/metrics/{metric_id}.py")
    if python_file.exists():
        files_to_remove.append(python_file)
    
    # 2. YAML configuration file  
    yaml_file = Path(f"metrics_hub/metrics/{metric_id}.yaml")
    if yaml_file.exists():
        files_to_remove.append(yaml_file)
    
    # 3. Test file
    test_file = Path(f"tests/test_{metric_id}.py")
    if test_file.exists():
        files_to_remove.append(test_file)
    
    # 4. Deployment script
    deploy_file = Path(f"deploy_{metric_id}.py")
    if deploy_file.exists():
        files_to_remove.append(deploy_file)
    
    # 5. Requirements file (if exists)
    req_file = Path(f"{metric_id}_requirements.txt")
    if req_file.exists():
        files_to_remove.append(req_file)
    
    if not files_to_remove:
        click.echo(f"❌ No files found for metric '{metric_id}'")
        return
    
    # Show what will be removed
    click.echo(f"\n📋 Files to be removed ({len(files_to_remove)}):")
    for file_path in files_to_remove:
        click.echo(f"   🗃️  {file_path}")
    
    # Confirmation (unless --force is used)
    if not force:
        click.echo(f"\n⚠️  This action cannot be undone!")
        if not click.confirm(f"Are you sure you want to remove metric '{metric_id}' and all its files?"):
            click.echo("❌ Operation cancelled.")
            return
    
    # Remove files
    removed_count = 0
    errors = []
    
    for file_path in files_to_remove:
        try:
            file_path.unlink()
            click.echo(f"✅ Removed: {file_path}")
            removed_count += 1
        except Exception as e:
            error_msg = f"Failed to remove {file_path}: {e}"
            errors.append(error_msg)
            click.echo(f"❌ {error_msg}")
    
    # Summary
    click.echo(f"\n📊 Removal Summary:")
    click.echo(f"   ✅ Successfully removed: {removed_count} files")
    if errors:
        click.echo(f"   ❌ Errors: {len(errors)} files")
        click.echo("\n🔧 Errors encountered:")
        for error in errors:
            click.echo(f"   • {error}")
    
    if removed_count > 0:
        click.echo(f"\n🎉 Metric '{metric_id}' has been removed!")
        click.echo("💡 Run 'metrics-hub list' to see remaining metrics.")
        
        # Suggest reloading if in interactive environment
        click.echo("\n📝 Note: If using interactive Python/Jupyter:")
        click.echo("   - Restart kernel to clear imported modules")
        click.echo("   - Registry will auto-update on next metrics-hub command")
    else:
        click.echo(f"\n❌ No files were successfully removed for metric '{metric_id}'.")


def _clean_metric_id(name: str, category: str) -> str:
    """Create clean metric ID from name and category."""
    clean_name = name.lower().replace(' ', '_').replace('-', '_')
    clean_category = category.lower().replace(' ', '_').replace('-', '_')
    return f"{clean_category}_{clean_name}"


def _create_function_name(name: str) -> str:
    """Create function name from metric name."""
    clean_name = name.lower().replace(' ', '_').replace('-', '_')
    return f"calculate_{clean_name}"


def _get_template_config(template_type: str) -> Tuple[List[Dict], List[Dict], List[Dict]]:
    """Get predefined template configurations."""
    
    if template_type == 'simple':
        inputs = [
            {'name': 'value', 'type': 'float', 'required': True, 'description': 'Input value for calculation'}
        ]
        outputs = [
            {'name': 'result', 'type': 'float', 'description': 'Calculated result'}
        ]
        data_sources = []
    
    elif template_type == 'dataframe':
        inputs = [
            {'name': 'data_source', 'type': 'string', 'required': True, 'description': 'Database connection string'},
            {'name': 'query', 'type': 'string', 'required': True, 'description': 'SQL query to execute'},
            {'name': 'filters', 'type': 'object', 'required': False, 'description': 'Additional filters to apply'}
        ]
        outputs = [
            {'name': 'result_table', 'type': 'dataframe', 'description': 'Query results as DataFrame'},
            {'name': 'summary_stats', 'type': 'object', 'description': 'Summary statistics'}
        ]
        data_sources = [
            {'name': 'primary_db', 'type': 'database', 'connection': 'postgresql://user:pass@host/db'}
        ]
    
    elif template_type == 'plotly':
        inputs = [
            {'name': 'data', 'type': 'dataframe', 'required': True, 'description': 'Input data for visualization'},
            {'name': 'chart_type', 'type': 'string', 'default': 'line', 'description': 'Type of chart to create'},
            {'name': 'title', 'type': 'string', 'required': False, 'description': 'Chart title'}
        ]
        outputs = [
            {'name': 'chart', 'type': 'plotly_figure', 'description': 'Interactive chart'},
            {'name': 'data_table', 'type': 'plotly_table', 'description': 'Data as interactive table'}
        ]
        data_sources = []
    
    elif template_type == 'multi_source':
        inputs = [
            {'name': 'analysis_config', 'type': 'object', 'required': True, 'description': 'Configuration for analysis sources'},
            {'name': 'date_range', 'type': 'object', 'required': True, 'description': 'Date range for analysis'},
            {'name': 'filters', 'type': 'object', 'required': False, 'description': 'Additional filters'}
        ]
        outputs = [
            {'name': 'analysis_report', 'type': 'dataframe', 'description': 'Main analysis results'},
            {'name': 'trend_chart', 'type': 'plotly_figure', 'description': 'Trend visualization'},
            {'name': 'summary_metrics', 'type': 'object', 'description': 'Key metrics summary'}
        ]
        data_sources = [
            {'name': 'primary_db', 'type': 'database', 'connection': 'postgresql://user:pass@host/db'},
            {'name': 'external_api', 'type': 'api', 'endpoint': 'https://api.example.com'},
            {'name': 'reference_files', 'type': 'file', 'path': '/data/reference/'}
        ]
    
    return inputs, outputs, data_sources


def _interactive_config() -> Tuple[List[Dict], List[Dict], List[Dict]]:
    """Interactive configuration for complex metrics."""
    click.echo("\n📝 Interactive Configuration")
    click.echo("Define your metric parameters step by step.\n")
    
    # Inputs
    inputs = []
    click.echo("Input Parameters:")
    while True:
        param_name = click.prompt("Parameter name (or 'done' to finish)", default="done")
        if param_name.lower() == 'done':
            break
        
        param_type = click.prompt("Parameter type", 
                                type=click.Choice(['string', 'integer', 'float', 'boolean', 'array', 'object']),
                                default='string')
        required = click.confirm("Required parameter?", default=True)
        description = click.prompt("Description", default="")
        
        param_config = {
            'name': param_name,
            'type': param_type,
            'required': required,
            'description': description
        }
        
        if not required:
            default_val = click.prompt("Default value (optional)", default="", show_default=False)
            if default_val:
                param_config['default'] = default_val
        
        inputs.append(param_config)
    
    # Outputs  
    outputs = []
    click.echo("\nOutput Specifications:")
    while True:
        output_name = click.prompt("Output name (or 'done' to finish)", default="result")
        if output_name.lower() == 'done':
            break
        
        output_type = click.prompt("Output type",
                                 type=click.Choice(['string', 'integer', 'float', 'dataframe', 'plotly_figure', 'object']),
                                 default='object')
        description = click.prompt("Description", default="")
        
        outputs.append({
            'name': output_name,
            'type': output_type,
            'description': description
        })
    
    # Data Sources
    data_sources = []
    if click.confirm("\nDoes this metric use external data sources?", default=False):
        click.echo("Data Sources:")
        while True:
            source_name = click.prompt("Data source name (or 'done' to finish)", default="done")
            if source_name.lower() == 'done':
                break
            
            source_type = click.prompt("Source type",
                                     type=click.Choice(['database', 'api', 'file']),
                                     default='database')
            
            if source_type == 'database':
                connection = click.prompt("Connection string", default="postgresql://user:pass@host/db")
                data_sources.append({'name': source_name, 'type': source_type, 'connection': connection})
            elif source_type == 'api':
                endpoint = click.prompt("API endpoint", default="https://api.example.com")
                data_sources.append({'name': source_name, 'type': source_type, 'endpoint': endpoint})
            else:  # file
                path = click.prompt("File path", default="/data/")
                data_sources.append({'name': source_name, 'type': source_type, 'path': path})
    
    return inputs, outputs, data_sources


def _generate_metric_files(metric_id: str, function_name: str, name: str, category: str,
                          description: str, template: str, inputs: List[Dict], outputs: List[Dict],
                          data_sources: List[Dict], complex: bool):
    """Generate all files for a metric within the package structure."""
    
    # Ensure directories exist
    metrics_dir = Path("metrics_hub/metrics")
    tests_dir = Path("tests")
    tests_dir.mkdir(exist_ok=True)
    
    # Generate YAML configuration
    yaml_config = {
        'id': metric_id,
        'name': name,
        'description': description,
        'category': category,
        'template': template,
        'inputs': inputs,
        'outputs': outputs,
        'data_sources': data_sources
    }
    
    yaml_path = metrics_dir / f"{metric_id}.yaml"
    with open(yaml_path, 'w') as f:
        yaml.dump(yaml_config, f, default_flow_style=False, indent=2)
    
    # Generate Python implementation
    python_code = _generate_python_code(metric_id, function_name, name, description, 
                                       inputs, outputs, data_sources, template, complex)
    
    python_path = metrics_dir / f"{metric_id}.py"
    with open(python_path, 'w') as f:
        f.write(python_code)
    
    # Generate test file
    test_code = _generate_test_code(metric_id, function_name, inputs, outputs)
    test_path = tests_dir / f"test_{metric_id}.py"
    with open(test_path, 'w') as f:
        f.write(test_code)
    
    # Generate deployment script
    deploy_code = _generate_deploy_script(metric_id, function_name)
    deploy_path = Path(f"deploy_{metric_id}.py")
    with open(deploy_path, 'w') as f:
        f.write(deploy_code)


def _generate_python_code(metric_id: str, function_name: str, name: str, description: str,
                         inputs: List[Dict], outputs: List[Dict], data_sources: List[Dict],
                         template: str, complex: bool) -> str:
    """Generate Python implementation code."""
    
    # Determine required imports
    imports = ['import pandas as pd', 'import numpy as np', 'import logging']
    
    output_types = [out.get('type', '') for out in outputs]
    if any('plotly' in ot for ot in output_types):
        imports.extend(['import plotly.graph_objects as go', 'import plotly.express as px'])
    
    source_types = [ds.get('type', '') for ds in data_sources]
    if 'database' in source_types:
        imports.append('import sqlalchemy as sa')
    if 'api' in source_types:
        imports.append('import requests')
    
    # Generate function signature
    params = []
    for inp in inputs:
        param_type = _get_python_type_hint(inp['type'])
        if inp.get('required', True):
            params.append(f"{inp['name']}: {param_type}")
        else:
            default_val = _format_default_value(inp.get('default'))
            params.append(f"{inp['name']}: {param_type} = {default_val}")
    
    # Generate return type hint
    if len(outputs) == 1:
        return_type = _get_python_type_hint(outputs[0]['type'])
    else:
        return_type = "Dict[str, Any]"
    
    # Generate function body
    if template == 'simple':
        body = _generate_simple_body(inputs, outputs)
    elif template == 'dataframe':
        body = _generate_dataframe_body(inputs, outputs, data_sources)
    elif template == 'plotly':
        body = _generate_plotly_body(inputs, outputs)
    elif template == 'multi_source':
        body = _generate_multi_source_body(inputs, outputs, data_sources)
    else:
        body = _generate_simple_body(inputs, outputs)
    
    return f'''"""
{description}

Generated using the metrics-hub scaffolding system.
"""

{chr(10).join(imports)}
from metrics_hub import register_metric
from typing import Dict, Any, Optional, Union, List

logger = logging.getLogger(__name__)


@register_metric("{metric_id}")
def {function_name}({', '.join(params)}) -> {return_type}:
    """
    {description}
    
    Args:
{chr(10).join([f"        {inp['name']}: {inp.get('description', 'No description')}" for inp in inputs])}
    
    Returns:
{chr(10).join([f"        {out['name']}: {out.get('description', 'No description')}" for out in outputs])}
    """
    try:
        logger.info(f"Calculating {metric_id} with parameters: {{locals()}}")
        
{body}
        
        logger.info(f"Successfully calculated {metric_id}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to calculate {metric_id}: {{e}}")
        raise RuntimeError(f"Metric calculation failed: {{e}}") from e
'''


def _get_python_type_hint(param_type: str) -> str:
    """Get Python type hint for parameter type."""
    type_mapping = {
        'string': 'str',
        'integer': 'int', 
        'float': 'float',
        'boolean': 'bool',
        'array': 'List[Any]',
        'object': 'Dict[str, Any]',
        'dataframe': 'pd.DataFrame',
        'plotly_figure': 'go.Figure',
        'plotly_table': 'go.Figure'
    }
    return type_mapping.get(param_type, 'Any')


def _format_default_value(default: Any) -> str:
    """Format default value for Python code."""
    if default is None:
        return 'None'
    elif isinstance(default, str):
        return f'"{default}"'
    elif isinstance(default, (dict, list)):
        return json.dumps(default)
    else:
        return str(default)


def _generate_simple_body(inputs: List[Dict], outputs: List[Dict]) -> str:
    """Generate simple metric body."""
    if len(outputs) == 1:
        return f'''        # Simple calculation example
        result = {inputs[0]['name']} * 2
        
        # Add your calculation logic here'''
    else:
        return '''        # Multiple outputs example
        result = {
            'primary_result': value * 2,
            'secondary_result': value ** 2
        }
        
        # Add your calculation logic here'''


def _generate_dataframe_body(inputs: List[Dict], outputs: List[Dict], data_sources: List[Dict]) -> str:
    """Generate DataFrame-focused metric body."""
    return '''        # Database connection
        engine = sa.create_engine(data_source)
        
        # Execute query
        df = pd.read_sql(query, engine)
        
        # Apply filters if provided
        if filters:
            for column, value in filters.items():
                if column in df.columns:
                    df = df[df[column] == value]
        
        # Perform analysis
        summary_stats = {
            'row_count': len(df),
            'column_count': len(df.columns),
            'memory_usage': df.memory_usage(deep=True).sum()
        }
        
        # Add your analysis logic here
        
        result = {
            'result_table': df,
            'summary_stats': summary_stats
        }'''


def _generate_plotly_body(inputs: List[Dict], outputs: List[Dict]) -> str:
    """Generate Plotly-focused metric body."""
    return '''        # Create visualization based on chart type
        if chart_type == 'line':
            fig = px.line(data, title=title)
        elif chart_type == 'bar':
            fig = px.bar(data, title=title)
        elif chart_type == 'scatter':
            fig = px.scatter(data, title=title)
        else:
            fig = px.line(data, title=title)  # Default to line
        
        # Create data table
        table_fig = go.Figure(data=[go.Table(
            header=dict(values=list(data.columns)),
            cells=dict(values=[data[col] for col in data.columns])
        )])
        
        # Add your visualization logic here
        
        result = {
            'chart': fig,
            'data_table': table_fig
        }'''


def _generate_multi_source_body(inputs: List[Dict], outputs: List[Dict], data_sources: List[Dict]) -> str:
    """Generate multi-source metric body."""
    return '''        # Load data from multiple sources
        analysis_data = {}
        
        # Database source
        if 'primary_db' in analysis_config:
            engine = sa.create_engine(analysis_config['primary_db'])
            query = """
            SELECT * FROM your_table 
            WHERE date BETWEEN %(start_date)s AND %(end_date)s
            """
            analysis_data['db_data'] = pd.read_sql(query, engine, params=date_range)
        
        # API source
        if 'external_api' in analysis_config:
            response = requests.get(analysis_config['external_api'])
            response.raise_for_status()
            analysis_data['api_data'] = pd.DataFrame(response.json())
        
        # File source
        if 'reference_files' in analysis_config:
            analysis_data['reference_data'] = pd.read_csv(analysis_config['reference_files'])
        
        # Combine and analyze data
        combined_df = pd.concat([df for df in analysis_data.values()], ignore_index=True)
        
        # Create trend visualization
        trend_chart = px.line(combined_df, x='date', y='value', title='Trend Analysis')
        
        # Calculate summary metrics
        summary_metrics = {
            'total_records': len(combined_df),
            'date_range': f"{date_range.get('start_date')} to {date_range.get('end_date')}",
            'sources_used': len(analysis_data)
        }
        
        # Add your multi-source analysis logic here
        
        result = {
            'analysis_report': combined_df,
            'trend_chart': trend_chart,
            'summary_metrics': summary_metrics
        }'''


def _generate_result_type_tests(outputs: List[Dict]) -> str:
    """Generate pytest assertions for result types."""
    if len(outputs) == 1:
        output_type = outputs[0]['type']
        if output_type == 'dataframe':
            return "assert isinstance(result, pd.DataFrame)"
        elif output_type == 'plotly_figure':
            return "assert hasattr(result, 'data')  # Plotly figure check"
        elif output_type in ['string', 'str']:
            return "assert isinstance(result, str)"
        elif output_type in ['integer', 'int']:
            return "assert isinstance(result, int)"
        elif output_type == 'float':
            return "assert isinstance(result, (int, float))"
        elif output_type == 'boolean':
            return "assert isinstance(result, bool)"
        else:
            return "assert result is not None"
    else:
        # Multiple outputs - should be dict
        return "assert isinstance(result, dict)"


def _generate_invalid_params(inputs: List[Dict]) -> str:
    """Generate invalid parameters for testing."""
    if not inputs:
        return ""
    
    first_input = inputs[0]
    param_name = first_input['name']
    param_type = first_input['type']
    
    # Generate invalid value based on expected type
    if param_type in ['string', 'str']:
        return f"{param_name}=12345"  # Number instead of string
    elif param_type in ['integer', 'int']:
        return f"{param_name}='not_a_number'"  # String instead of int
    elif param_type == 'float':
        return f"{param_name}='not_a_float'"  # String instead of float
    elif param_type == 'boolean':
        return f"{param_name}='not_a_bool'"  # String instead of bool
    elif param_type == 'dataframe':
        return f"{param_name}='not_a_dataframe'"  # String instead of DataFrame
    else:
        return f"{param_name}=None"  # None for any other type


def _generate_output_structure_tests(outputs: List[Dict]) -> str:
    """Generate pytest assertions for output structure."""
    if len(outputs) == 1:
        return "# Single output - structure validated by type test above"
    
    tests = []
    for output in outputs:
        output_name = output['name']
        tests.append(f"assert '{output_name}' in result")
    
    return "\n        ".join(tests)


def _generate_test_code(metric_id: str, function_name: str, inputs: List[Dict], outputs: List[Dict] = None) -> str:
    """Generate test file for the metric."""
    
    if outputs is None:
        outputs = [{'name': 'result', 'type': 'object', 'description': 'Default result'}]
    
    # Generate test data based on input types
    test_params = []
    for inp in inputs:
        param_name = inp['name']
        param_type = inp['type']
        
        if param_type == 'string':
            test_params.append(f"{param_name}='test_value'")
        elif param_type == 'integer':
            test_params.append(f"{param_name}=42")
        elif param_type == 'float':
            test_params.append(f"{param_name}=3.14")
        elif param_type == 'boolean':
            test_params.append(f"{param_name}=True")
        elif param_type == 'array':
            test_params.append(f"{param_name}=[1, 2, 3]")
        elif param_type == 'object':
            test_params.append(f"{param_name}={{'key': 'value'}}")
        elif param_type == 'dataframe':
            test_params.append(f"{param_name}=pd.DataFrame({{'col1': [1, 2, 3], 'col2': ['a', 'b', 'c']}})")
    
    return f'''"""
Tests for {metric_id} metric.

Generated using the metrics-hub scaffolding system.
Uses pytest framework exclusively for all testing needs.
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, Mock  # Only for mocking, not test structure

from metrics_hub.metrics.{metric_id} import {function_name}


class Test{function_name.replace('_', '').title()}:
    """Test suite for {function_name} using pytest."""
    
    @pytest.fixture
    def sample_inputs(self):
        """Provide sample inputs for testing."""
        return {{{', '.join([f'"{inp["name"]}": {"42" if inp["type"] in ["integer", "float"] else '"test_value"'}' for inp in inputs])}}}
    
    def test_basic_calculation(self, sample_inputs):
        """Test basic metric calculation with valid inputs."""
        result = {function_name}(**sample_inputs)
        
        assert result is not None
        # Add your specific assertions here
        
        # Test return type based on expected outputs
        {_generate_result_type_tests(outputs)}
    
    def test_input_validation(self):
        """Test input validation with pytest.raises."""
        # Test with missing required parameters
        with pytest.raises((ValueError, TypeError)):
            {function_name}()
        
        # Test with invalid parameter types
        with pytest.raises((ValueError, TypeError)):
            {function_name}({_generate_invalid_params(inputs)})
    
    @pytest.mark.parametrize("test_input,expected_error", [
        (None, ValueError),
        ("invalid_type", TypeError),
        # Add more parameter test cases here
    ])
    def test_parameter_validation(self, test_input, expected_error):
        """Test various parameter validation scenarios."""
        with pytest.raises(expected_error):
            # Adjust this based on your metric's first parameter
            {function_name}(test_input)
    
    def test_error_handling_and_logging(self):
        """Test error handling and logging using pytest."""
        with patch('metrics_hub.metrics.{metric_id}.logger') as mock_logger:
            try:
                # Test with valid inputs first
                result = {function_name}({', '.join(test_params)})
                assert result is not None
                mock_logger.info.assert_called()
            except Exception:
                # If there's an error, verify it's logged
                mock_logger.error.assert_called()
    
    def test_result_structure(self, sample_inputs):
        """Test that result has expected structure."""
        result = {function_name}(**sample_inputs)
        
        # Verify result structure based on your metric's outputs
        {_generate_output_structure_tests(outputs)}


class TestIntegration:
    """Integration tests with the metrics hub system using pytest."""
    
    def test_metric_registration(self):
        """Test that metric is properly registered."""
        from metrics_hub import get_metric
        
        metric_func = get_metric("{metric_id}")
        assert metric_func is not None
        assert metric_func.__name__ == "{function_name}"
    
    def test_metric_config_loading(self):
        """Test that metric configuration is loaded correctly."""
        from metrics_hub.core import get_registry
        
        registry = get_registry()
        config = registry.get_config("{metric_id}")
        
        assert config is not None
        assert config['id'] == "{metric_id}"
        assert 'inputs' in config
        assert 'outputs' in config
        
        # Validate specific configuration elements
        assert len(config['inputs']) >= {len(inputs)}
        assert len(config['outputs']) >= {len(outputs)}
    
    def test_api_integration(self):
        """Test metric through API interface using FastAPI TestClient."""
        pytest.importorskip("fastapi")  # Skip if FastAPI not available
        
        from metrics_hub.api import create_api_app
        from fastapi.testclient import TestClient
        
        app = create_api_app()
        
        with TestClient(app) as client:
            # Test metric listing endpoint
            response = client.get("/metrics")
            assert response.status_code == 200
            
            metrics = response.json()
            metric_ids = [m['id'] for m in metrics]
            assert "{metric_id}" in metric_ids
            
            # Test metric calculation endpoint
            test_payload = {{
                "metric_id": "{metric_id}",
                "inputs": {{{', '.join([f'"{inp["name"]}": "test_value"' for inp in inputs])}}}
            }}
            
            response = client.post("/calculate", json=test_payload)
            assert response.status_code == 200
            
            result = response.json()
            assert result['success'] is True
            assert result['metric_id'] == "{metric_id}"
    
    @pytest.mark.slow  # Mark for slow tests that can be skipped
    def test_dashboard_integration(self):
        """Test metric integration with dashboard."""
        pytest.importorskip("dash")  # Skip if Dash not available
        
        from metrics_hub.dashboard import create_dashboard_app
        
        # Test that dashboard can be created with this metric
        app = create_dashboard_app()
        assert app is not None
        
        # Test that metric appears in dashboard registry
        from metrics_hub import list_metrics
        metrics = list_metrics()
        metric_ids = [m['id'] for m in metrics]
        assert "{metric_id}" in metric_ids


# Pytest configuration and fixtures
@pytest.fixture(scope="session")
def test_metric_id():
    """Provide the metric ID for session-wide tests."""
    return "{metric_id}"


@pytest.fixture(scope="session") 
def test_function():
    """Provide the metric function for session-wide tests."""
    return {function_name}
'''


def _generate_deploy_script(metric_id: str, function_name: str) -> str:
    """Generate Posit Connect deployment script."""
    
    return f'''"""
Posit Connect deployment script for {metric_id}.

This script creates a FastAPI application specifically for this metric
that can be deployed to Posit Connect.
"""

import os
from metrics_hub.api import create_api_app

# Import the metric to ensure it's registered
from metrics_hub.metrics.{metric_id} import {function_name}

# Create the FastAPI app with all registered metrics
app = create_api_app()

# Add custom root endpoint for this specific metric
@app.get("/", tags=["Metric Info"])
async def metric_info():
    """Get information about this specific metric deployment."""
    return {{
        "metric_id": "{metric_id}",
        "function_name": "{function_name}",
        "status": "active",
        "endpoints": [
            "/metrics",
            "/calculate",
            "/calculate/{metric_id}",
            "/calculate/{metric_id}/html",
            "/calculate/{metric_id}/csv",
            "/docs"
        ],
        "description": "Metrics Hub deployment for {metric_id}"
    }}

# For local testing
if __name__ == "__main__":
    import uvicorn
    
    # Configuration
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    reload = os.environ.get("RELOAD", "false").lower() == "true"
    
    print(f"Starting {metric_id} deployment...")
    print(f"URL: http://{{host}}:{{port}}")
    print(f"API Documentation: http://{{host}}:{{port}}/docs")
    print(f"Metric HTML: http://{{host}}:{{port}}/calculate/{metric_id}/html")
    
    uvicorn.run("deploy_{metric_id}:app", host=host, port=port, reload=reload)
'''


if __name__ == '__main__':
    cli()