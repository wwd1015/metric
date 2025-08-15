"""
Dash dashboard for interactive metric testing.

Provides a web interface for testing metrics with dynamic form generation
and rich output visualization.
"""

import dash
from dash import dcc, html, Input, Output, State, dash_table, callback
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any, List, Optional
import json
import logging

from .core import get_registry

logger = logging.getLogger(__name__)


def create_dashboard_app() -> dash.Dash:
    """Create Dash application for metric testing."""
    
    app = dash.Dash(__name__, title="Metrics Hub Dashboard")
    registry = get_registry()
    
    app.layout = html.Div([
        html.Div([
            html.H1("Metrics Hub Dashboard", className="text-center mb-4"),
            html.P("Interactive testing environment for metrics with rich outputs", 
                   className="text-center text-muted mb-5")
        ], className="header-section"),
        
        html.Div([
            # Metric Selection Section
            html.Div([
                html.H3("Select Metric"),
                dcc.Dropdown(
                    id="metric-dropdown",
                    options=[],
                    placeholder="Choose a metric to test...",
                    className="mb-3"
                ),
                html.Div(id="metric-info", className="mb-4")
            ], className="metric-selection"),
            
            # Input Controls Section  
            html.Div([
                html.H3("Parameters"),
                html.Div(id="input-controls", className="mb-4")
            ], className="input-section"),
            
            # Action Buttons
            html.Div([
                html.Button("Calculate", id="calculate-btn", 
                           className="btn btn-primary me-2", disabled=True),
                html.Button("Clear", id="clear-btn", 
                           className="btn btn-secondary")
            ], className="action-buttons mb-4"),
            
            # Results Section
            html.Div([
                html.H3("Results"),
                dcc.Loading(
                    id="loading",
                    children=[
                        html.Div(id="results-display"),
                        html.Div(id="visualization")
                    ],
                    type="default"
                )
            ], className="results-section")
            
        ], className="main-content container")
    ])
    
    # Initialize metric options
    @app.callback(
        Output("metric-dropdown", "options"),
        Input("metric-dropdown", "id")
    )
    def load_metric_options(_):
        """Load available metrics into dropdown."""
        try:
            metrics = registry.list_all()
            return [
                {
                    "label": f"{m.get('name', m['id'])} ({m['id']})", 
                    "value": m['id']
                }
                for m in metrics
            ]
        except Exception as e:
            logger.error(f"Failed to load metrics: {e}")
            return []
    
    # Update metric info and input controls
    @app.callback(
        [Output("metric-info", "children"),
         Output("input-controls", "children"), 
         Output("calculate-btn", "disabled")],
        [Input("metric-dropdown", "value")]
    )
    def update_metric_selection(metric_id):
        """Update metric information and generate input controls."""
        if not metric_id:
            return "", "", True
        
        try:
            config = registry.get_config(metric_id)
            if not config:
                return "Metric configuration not found", "", True
            
            # Metric info display
            info_div = html.Div([
                html.H5(config.get('name', metric_id)),
                html.P(config.get('description', 'No description available')),
                html.Small(f"Category: {config.get('category', 'Unknown')}", 
                          className="text-muted")
            ], className="metric-info-box p-3 bg-light rounded")
            
            # Generate input controls
            controls = []
            inputs = config.get('inputs', [])
            
            if not inputs:
                controls.append(html.P("This metric requires no input parameters."))
            else:
                for input_param in inputs:
                    param_name = input_param['name']
                    param_type = input_param.get('type', 'string')
                    required = input_param.get('required', False)
                    default = input_param.get('default')
                    description = input_param.get('description', '')
                    
                    # Create appropriate input control
                    control = _create_input_control(param_name, param_type, default, description, required)
                    controls.append(control)
            
            return info_div, controls, False
            
        except Exception as e:
            logger.error(f"Failed to load metric {metric_id}: {e}")
            return f"Error loading metric: {e}", "", True
    
    # Calculate metric
    @app.callback(
        [Output("results-display", "children"),
         Output("visualization", "children")],
        [Input("calculate-btn", "n_clicks")],
        [State("metric-dropdown", "value")] + 
        [State({"type": "metric-input", "param": dash.dependencies.ALL}, "value")]
    )
    def calculate_metric(n_clicks, metric_id, input_values):
        """Calculate the selected metric with provided inputs."""
        if not n_clicks or not metric_id:
            return "", ""
        
        try:
            # Get metric configuration to map input values
            config = registry.get_config(metric_id)
            inputs = config.get('inputs', []) if config else []
            
            # Build kwargs from input values
            kwargs = {}
            for i, input_param in enumerate(inputs):
                if i < len(input_values) and input_values[i] is not None:
                    param_name = input_param['name']
                    param_type = input_param.get('type', 'string')
                    value = _convert_input_value(input_values[i], param_type)
                    kwargs[param_name] = value
            
            # Call the metric
            result = registry.call_metric(metric_id, **kwargs)
            
            # Create result display and visualization
            result_display = _create_result_display(result, config)
            visualization = _create_visualization(result, config)
            
            return result_display, visualization
            
        except Exception as e:
            logger.error(f"Calculation failed: {e}")
            error_div = html.Div([
                html.H5("Calculation Error", className="text-danger"),
                html.P(str(e), className="text-danger"),
                html.Small("Check the logs for more details.", className="text-muted")
            ], className="alert alert-danger")
            return error_div, ""
    
    # Clear results
    @app.callback(
        [Output("results-display", "children", allow_duplicate=True),
         Output("visualization", "children", allow_duplicate=True)],
        [Input("clear-btn", "n_clicks")],
        prevent_initial_call=True
    )
    def clear_results(n_clicks):
        """Clear displayed results."""
        if n_clicks:
            return "", ""
        return dash.no_update, dash.no_update
    
    return app


def _create_input_control(param_name: str, param_type: str, default: Any, 
                         description: str, required: bool) -> html.Div:
    """Create appropriate input control based on parameter type."""
    
    label_text = param_name
    if required:
        label_text += " *"
    
    label = html.Label(label_text, className="form-label")
    
    if description:
        help_text = html.Small(description, className="form-text text-muted")
    else:
        help_text = ""
    
    # Choose control type based on parameter type
    if param_type in ['integer', 'float']:
        control = dcc.Input(
            id={"type": "metric-input", "param": param_name},
            type="number",
            value=default,
            placeholder=f"Enter {param_name}",
            className="form-control"
        )
    elif param_type == 'boolean':
        control = dcc.Checklist(
            id={"type": "metric-input", "param": param_name},
            options=[{"label": f"Enable {param_name}", "value": True}],
            value=[True] if default else [],
            className="form-check"
        )
    elif param_type == 'array':
        control = dcc.Textarea(
            id={"type": "metric-input", "param": param_name},
            value=json.dumps(default) if default else "",
            placeholder="Enter JSON array or comma-separated values",
            className="form-control",
            rows=3
        )
    elif param_type == 'object':
        control = dcc.Textarea(
            id={"type": "metric-input", "param": param_name},
            value=json.dumps(default, indent=2) if default else "",
            placeholder="Enter JSON object",
            className="form-control",
            rows=4
        )
    else:  # string or unknown
        control = dcc.Input(
            id={"type": "metric-input", "param": param_name},
            type="text",
            value=default,
            placeholder=f"Enter {param_name}",
            className="form-control"
        )
    
    return html.Div([
        label,
        control,
        help_text
    ], className="mb-3")


def _convert_input_value(value: Any, param_type: str) -> Any:
    """Convert input value to appropriate type."""
    if value is None or value == "":
        return None
    
    try:
        if param_type == 'integer':
            return int(value)
        elif param_type == 'float':
            return float(value)
        elif param_type == 'boolean':
            return bool(value) if isinstance(value, list) else bool(value)
        elif param_type in ['array', 'object']:
            if isinstance(value, str):
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    # Try comma-separated for arrays
                    if param_type == 'array':
                        return [x.strip() for x in value.split(',') if x.strip()]
                    else:
                        raise ValueError(f"Invalid JSON for {param_type}")
            return value
        else:
            return str(value)
    except Exception as e:
        logger.error(f"Failed to convert value {value} to {param_type}: {e}")
        return value


def _create_result_display(result: Any, config: Optional[Dict[str, Any]]) -> html.Div:
    """Create display for calculation results."""
    
    if result is None:
        return html.P("No results returned", className="text-muted")
    
    components = []
    
    if isinstance(result, (int, float)):
        # Simple numeric result
        components.append(html.H4(f"Result: {result}", className="text-success"))
    
    elif isinstance(result, str):
        # String result
        components.append(html.Pre(result, className="bg-light p-3 rounded"))
    
    elif isinstance(result, pd.DataFrame):
        # DataFrame result
        components.extend([
            html.H5("Data Table"),
            html.P(f"Shape: {result.shape[0]} rows × {result.shape[1]} columns"),
            dash_table.DataTable(
                data=result.head(100).to_dict('records'),  # Limit to first 100 rows
                columns=[{"name": str(i), "id": str(i)} for i in result.columns],
                page_size=10,
                sort_action="native",
                filter_action="native",
                style_table={'overflowX': 'auto'},
                style_cell={'textAlign': 'left', 'minWidth': '100px'},
                style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'}
            )
        ])
    
    elif isinstance(result, dict):
        # Dictionary result - handle mixed outputs
        for key, value in result.items():
            components.append(html.H5(key.replace('_', ' ').title()))
            
            if isinstance(value, pd.DataFrame):
                components.extend([
                    html.P(f"Shape: {value.shape[0]} rows × {value.shape[1]} columns"),
                    dash_table.DataTable(
                        data=value.head(100).to_dict('records'),
                        columns=[{"name": str(i), "id": str(i)} for i in value.columns],
                        page_size=5,
                        style_table={'overflowX': 'auto'},
                        style_cell={'textAlign': 'left', 'minWidth': '80px'}
                    )
                ])
            elif isinstance(value, (int, float)):
                components.append(html.P(f"{value}", className="h4 text-primary"))
            elif isinstance(value, dict):
                components.append(html.Pre(json.dumps(value, indent=2), 
                                         className="bg-light p-3 rounded"))
            else:
                components.append(html.P(str(value)))
    
    else:
        # Other types
        components.append(html.Pre(str(result), className="bg-light p-3 rounded"))
    
    return html.Div(components, className="results-content")


def _create_visualization(result: Any, config: Optional[Dict[str, Any]]) -> html.Div:
    """Create visualization based on result type."""
    
    components = []
    
    if isinstance(result, (int, float)):
        # Create gauge chart for single values
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=result,
            title={'text': config.get('name', 'Metric Value') if config else 'Value'},
            gauge={'axis': {'range': [None, result * 1.5]}}
        ))
        components.append(dcc.Graph(figure=fig))
    
    elif isinstance(result, pd.DataFrame):
        # Create basic visualization for DataFrame
        if len(result.columns) >= 2:
            # Try to create a simple chart
            numeric_cols = result.select_dtypes(include=['number']).columns
            if len(numeric_cols) >= 1:
                fig = px.line(result.head(50), y=numeric_cols[0], 
                             title="Data Trend")
                components.append(dcc.Graph(figure=fig))
    
    elif isinstance(result, go.Figure):
        # Direct Plotly figure
        components.append(dcc.Graph(figure=result))
    
    elif isinstance(result, dict):
        # Handle mixed results
        for key, value in result.items():
            if isinstance(value, go.Figure):
                components.append(html.H5(key.replace('_', ' ').title()))
                components.append(dcc.Graph(figure=value))
            elif isinstance(value, pd.DataFrame) and len(value.columns) >= 2:
                numeric_cols = value.select_dtypes(include=['number']).columns
                if len(numeric_cols) >= 1:
                    fig = px.bar(value.head(20), y=numeric_cols[0], 
                               title=f"{key.replace('_', ' ').title()} - Data Chart")
                    components.append(html.H5(key.replace('_', ' ').title()))
                    components.append(dcc.Graph(figure=fig))
    
    return html.Div(components, className="visualization-content")


def run_dashboard(host: str = "127.0.0.1", port: int = 8050, debug: bool = False):
    """Run the dashboard server."""
    app = create_dashboard_app()
    app.run(host=host, port=port, debug=debug)