"""
Metrics Hub - Metric development and deployment package.

A streamlined package for developing, testing, and deploying complex metrics
with rich outputs including DataFrames and interactive Plotly visualizations.
"""

from .core import MetricRegistry, register_metric, get_metric, list_metrics, call_metric
from .api import create_api_app, run_api_server
from .dashboard import create_dashboard_app, run_dashboard

__version__ = "1.0.0"
__author__ = "Metrics Hub Team"

__all__ = [
    "MetricRegistry",
    "register_metric", 
    "get_metric",
    "list_metrics",
    "call_metric",
    "create_api_app",
    "run_api_server",
    "create_dashboard_app",
    "run_dashboard"
]