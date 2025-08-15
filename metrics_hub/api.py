"""
FastAPI interface for metrics with rich output support.
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Union
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly
import json
import logging

from .core import get_registry

logger = logging.getLogger(__name__)


class MetricRequest(BaseModel):
    """Request model for metric calculation."""
    metric_id: str = Field(..., description="Metric ID to calculate")
    inputs: Dict[str, Any] = Field(default_factory=dict, description="Input parameters")
    output_format: str = Field(default="json", description="Output format: json, html, csv")


class MetricResponse(BaseModel):
    """Response model for metric calculation."""
    metric_id: str
    result: Any
    result_type: str
    success: bool
    error: Optional[str] = None
    output_format: str = "json"


def create_api_app() -> FastAPI:
    """Create FastAPI application for metrics."""
    
    app = FastAPI(
        title="Metrics Hub API",
        description="API for complex metric calculations with rich outputs",
        version="1.0.0"
    )
    
    registry = get_registry()
    
    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "message": "Metrics Hub API", 
            "version": "1.0.0",
            "features": ["DataFrames", "Plotly Charts", "Complex Metrics"]
        }
    
    @app.get("/health")
    async def health_check():
        """Health check for Posit Connect."""
        return {"status": "healthy", "service": "metrics-hub"}
    
    @app.get("/metrics", response_model=List[Dict[str, Any]])
    async def list_metrics():
        """List all available metrics."""
        try:
            return registry.list_all()
        except Exception as e:
            logger.error(f"Failed to list metrics: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/metrics/{metric_id}")
    async def get_metric_info(metric_id: str):
        """Get metric configuration."""
        config = registry.get_config(metric_id)
        if not config:
            raise HTTPException(status_code=404, detail=f"Metric not found: {metric_id}")
        return config
    
    @app.post("/calculate")
    async def calculate_metric(request: MetricRequest):
        """Calculate a metric with rich output support."""
        try:
            result = registry.call_metric(request.metric_id, **request.inputs)
            result_type, processed_result = _process_result(result, request.output_format)
            
            return MetricResponse(
                metric_id=request.metric_id,
                result=processed_result,
                result_type=result_type,
                success=True,
                output_format=request.output_format
            )
            
        except ValueError as e:
            return MetricResponse(
                metric_id=request.metric_id,
                result=None,
                result_type="error",
                success=False,
                error=str(e),
                output_format=request.output_format
            )
        except Exception as e:
            logger.error(f"Calculation failed: {e}")
            return MetricResponse(
                metric_id=request.metric_id,
                result=None,
                result_type="error",
                success=False,
                error=f"Calculation error: {str(e)}",
                output_format=request.output_format
            )
    
    @app.get("/calculate/{metric_id}")
    async def calculate_metric_get(metric_id: str, output_format: str = "json", **params):
        """Calculate metric via GET request with rich outputs."""
        try:
            # Convert query parameters
            inputs = _convert_query_params(metric_id, params)
            
            result = registry.call_metric(metric_id, **inputs)
            result_type, processed_result = _process_result(result, output_format)
            
            # Return appropriate response type
            if output_format == "html" and result_type == "plotly":
                return HTMLResponse(content=processed_result)
            elif output_format == "csv" and result_type == "dataframe":
                from fastapi.responses import Response
                return Response(content=processed_result, media_type="text/csv")
            else:
                return MetricResponse(
                    metric_id=metric_id,
                    result=processed_result,
                    result_type=result_type,
                    success=True,
                    output_format=output_format
                )
                
        except Exception as e:
            logger.error(f"GET calculation failed: {e}")
            return MetricResponse(
                metric_id=metric_id,
                result=None,
                result_type="error",
                success=False,
                error=str(e),
                output_format=output_format
            )
    
    @app.get("/calculate/{metric_id}/html")
    async def calculate_metric_html(metric_id: str, **params):
        """Calculate metric and return HTML visualization."""
        try:
            inputs = _convert_query_params(metric_id, params)
            result = registry.call_metric(metric_id, **inputs)
            
            # Generate HTML output
            html_content = _generate_html_output(metric_id, result, inputs)
            return HTMLResponse(content=html_content)
            
        except Exception as e:
            logger.error(f"HTML calculation failed: {e}")
            error_html = f"<html><body><h1>Error</h1><p>{str(e)}</p></body></html>"
            return HTMLResponse(content=error_html, status_code=500)
    
    @app.get("/calculate/{metric_id}/csv")
    async def calculate_metric_csv(metric_id: str, **params):
        """Calculate metric and return CSV if result is DataFrame."""
        try:
            inputs = _convert_query_params(metric_id, params)
            result = registry.call_metric(metric_id, **inputs)
            
            if isinstance(result, pd.DataFrame):
                from fastapi.responses import Response
                csv_content = result.to_csv(index=False)
                return Response(
                    content=csv_content, 
                    media_type="text/csv",
                    headers={"Content-Disposition": f"attachment; filename={metric_id}.csv"}
                )
            else:
                raise HTTPException(status_code=400, detail="Result is not a DataFrame")
                
        except Exception as e:
            logger.error(f"CSV calculation failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    return app


def _process_result(result: Any, output_format: str = "json") -> tuple[str, Any]:
    """Process result based on type and output format."""
    
    if isinstance(result, pd.DataFrame):
        if output_format == "csv":
            return "dataframe", result.to_csv(index=False)
        elif output_format == "html":
            return "dataframe", result.to_html(classes="table table-striped")
        else:
            # Convert to JSON-serializable format
            return "dataframe", result.to_dict(orient="records")
    
    elif isinstance(result, go.Figure):
        if output_format == "html":
            return "plotly", result.to_html(include_plotlyjs=True, full_html=True)
        else:
            # Return plotly JSON
            return "plotly", result.to_dict()
    
    elif hasattr(result, 'to_plotly_json'):
        # Handle other plotly objects
        if output_format == "html":
            return "plotly", result.to_html(include_plotlyjs=True, full_html=True)
        else:
            return "plotly", result.to_plotly_json()
    
    elif isinstance(result, dict):
        # Check if dict contains DataFrames or Plotly objects
        processed_dict = {}
        contains_complex = False
        
        for key, value in result.items():
            if isinstance(value, pd.DataFrame):
                contains_complex = True
                if output_format == "json":
                    processed_dict[key] = value.to_dict(orient="records")
                else:
                    processed_dict[key] = value.to_html(classes="table table-striped")
            elif isinstance(value, go.Figure):
                contains_complex = True
                if output_format == "html":
                    processed_dict[key] = value.to_html(include_plotlyjs=True, div_id=f"plot-{key}")
                else:
                    processed_dict[key] = value.to_dict()
            else:
                processed_dict[key] = value
        
        return "complex" if contains_complex else "dict", processed_dict
    
    else:
        # Simple values (int, float, str, list, etc.)
        return "simple", result


def _convert_query_params(metric_id: str, params: dict) -> dict:
    """Convert query parameters to appropriate types based on metric config."""
    registry = get_registry()
    config = registry.get_config(metric_id)
    
    inputs = {}
    if config:
        for input_param in config.get('inputs', []):
            param_name = input_param['name']
            if param_name in params:
                param_type = input_param.get('type', 'string')
                value = params[param_name]
                
                # Enhanced type conversion
                if param_type == 'integer':
                    inputs[param_name] = int(value)
                elif param_type == 'float':
                    inputs[param_name] = float(value)
                elif param_type == 'boolean':
                    inputs[param_name] = value.lower() in ('true', '1', 'yes')
                elif param_type == 'array':
                    if isinstance(value, str):
                        # Try to parse as JSON first, then fall back to comma-separated
                        try:
                            inputs[param_name] = json.loads(value)
                        except:
                            inputs[param_name] = [x.strip() for x in value.split(',') if x.strip()]
                    else:
                        inputs[param_name] = value
                elif param_type == 'object':
                    if isinstance(value, str):
                        try:
                            inputs[param_name] = json.loads(value)
                        except:
                            inputs[param_name] = {'value': value}
                    else:
                        inputs[param_name] = value
                else:
                    inputs[param_name] = value
    else:
        # No config available, pass through as strings
        inputs = dict(params)
    
    return inputs


def _generate_html_output(metric_id: str, result: Any, inputs: dict) -> str:
    """Generate comprehensive HTML output for metric results."""
    
    registry = get_registry()
    config = registry.get_config(metric_id)
    metric_name = config.get('name', metric_id) if config else metric_id
    
    html_parts = [
        "<!DOCTYPE html>",
        "<html>",
        "<head>",
        f"<title>{metric_name} - Results</title>",
        "<script src='https://cdn.plot.ly/plotly-latest.min.js'></script>",
        "<link href='https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css' rel='stylesheet'>",
        "<style>",
        ".metric-container { margin: 20px; }",
        ".metric-header { background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px; }",
        ".result-section { margin-bottom: 30px; }",
        "</style>",
        "</head>",
        "<body>",
        "<div class='container metric-container'>",
        f"<div class='metric-header'><h1>{metric_name}</h1>",
        f"<p class='text-muted'>Metric ID: {metric_id}</p>",
    ]
    
    if config and config.get('description'):
        html_parts.append(f"<p>{config['description']}</p>")
    
    html_parts.append("</div>")
    
    # Show inputs
    html_parts.extend([
        "<div class='result-section'>",
        "<h3>Inputs</h3>",
        "<table class='table table-sm'>",
        "<thead><tr><th>Parameter</th><th>Value</th></tr></thead>",
        "<tbody>"
    ])
    
    for key, value in inputs.items():
        html_parts.append(f"<tr><td>{key}</td><td>{str(value)}</td></tr>")
    
    html_parts.extend(["</tbody>", "</table>", "</div>"])
    
    # Show results
    html_parts.extend([
        "<div class='result-section'>",
        "<h3>Results</h3>"
    ])
    
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
            else:
                html_parts.append(f"<p>{str(value)}</p>")
    else:
        html_parts.append(f"<pre>{str(result)}</pre>")
    
    html_parts.extend([
        "</div>",
        "</div>",
        "</body>",
        "</html>"
    ])
    
    return "\\n".join(html_parts)


def run_api_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """Run the API server."""
    import uvicorn
    app = create_api_app()
    uvicorn.run(app, host=host, port=port, reload=reload)