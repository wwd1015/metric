"""
Core metric registry and function management.

Handles metric registration, discovery, and execution within the package.
"""

import yaml
import importlib
import inspect
from pathlib import Path
from typing import Dict, Any, List, Callable, Optional
import logging

logger = logging.getLogger(__name__)


class MetricRegistry:
    """Registry for metric functions within the package."""
    
    def __init__(self, metrics_module: str = "metrics_hub.metrics"):
        self.metrics_module = metrics_module
        self.metrics: Dict[str, Dict[str, Any]] = {}
        self._functions: Dict[str, Callable] = {}
        self.load_metrics()
    
    def load_metrics(self):
        """Load all metrics from the metrics module and config files."""
        self._load_configurations()
        self._load_functions()
    
    def _load_configurations(self):
        """Load YAML configurations from the metrics module."""
        try:
            # Get the metrics module path
            metrics_module = importlib.import_module(self.metrics_module)
            metrics_path = Path(metrics_module.__file__).parent
            
            # Load all YAML files in the metrics directory
            for yaml_file in metrics_path.glob("**/*.yaml"):
                try:
                    with open(yaml_file, 'r') as f:
                        config = yaml.safe_load(f)
                        if config and 'id' in config:
                            self.metrics[config['id']] = config
                            logger.debug(f"Loaded metric config: {config['id']}")
                except Exception as e:
                    logger.error(f"Failed to load {yaml_file}: {e}")
        except ImportError:
            logger.warning(f"Metrics module '{self.metrics_module}' not found")
    
    def _load_functions(self):
        """Load Python functions from the metrics module."""
        try:
            # Import the metrics module
            metrics_module = importlib.import_module(self.metrics_module)
            
            # Recursively import all submodules
            metrics_path = Path(metrics_module.__file__).parent
            for py_file in metrics_path.glob("**/*.py"):
                if py_file.name.startswith('__'):
                    continue
                
                try:
                    # Convert file path to module path
                    # Calculate relative path from the metrics directory
                    relative_path = py_file.relative_to(metrics_path)
                    # Build the full module path including the metrics_module prefix
                    if relative_path.parts:
                        module_name = str(relative_path.with_suffix('')).replace('/', '.').replace('\\', '.')
                        module_path = f"{self.metrics_module}.{module_name}"
                    else:
                        module_path = self.metrics_module
                    
                    # Import the module
                    module = importlib.import_module(module_path)
                    
                    # Find metric functions
                    for name, obj in inspect.getmembers(module, inspect.isfunction):
                        if hasattr(obj, '__metric_id__'):
                            metric_id = obj.__metric_id__
                            self._functions[metric_id] = obj
                            logger.debug(f"Loaded metric function: {metric_id}")
                            
                except Exception as e:
                    logger.error(f"Failed to import {py_file}: {e}")
                    
        except ImportError:
            logger.warning(f"Metrics module '{self.metrics_module}' not found")
    
    def get_function(self, metric_id: str) -> Optional[Callable]:
        """Get metric function by ID."""
        return self._functions.get(metric_id)
    
    def get_config(self, metric_id: str) -> Optional[Dict[str, Any]]:
        """Get metric configuration by ID."""
        return self.metrics.get(metric_id)
    
    def list_all(self) -> List[Dict[str, Any]]:
        """List all available metrics."""
        return list(self.metrics.values())
    
    def call_metric(self, metric_id: str, **kwargs) -> Any:
        """Call a metric function with given parameters."""
        func = self.get_function(metric_id)
        if not func:
            raise ValueError(f"Metric function not found: {metric_id}")
        
        config = self.get_config(metric_id)
        if config:
            # Apply defaults from config
            for input_param in config.get('inputs', []):
                param_name = input_param['name']
                if param_name not in kwargs and 'default' in input_param:
                    kwargs[param_name] = input_param['default']
        
        return func(**kwargs)


# Global registry instance
_registry = None

def get_registry() -> MetricRegistry:
    """Get or create global metric registry."""
    global _registry
    if _registry is None:
        _registry = MetricRegistry()
    return _registry


def register_metric(metric_id: str):
    """Decorator to register a metric function."""
    def decorator(func: Callable):
        func.__metric_id__ = metric_id
        return func
    return decorator


def get_metric(metric_id: str) -> Optional[Callable]:
    """Get metric function by ID."""
    return get_registry().get_function(metric_id)


def list_metrics() -> List[Dict[str, Any]]:
    """List all available metrics."""
    return get_registry().list_all()


def call_metric(metric_id: str, **kwargs) -> Any:
    """Call a metric function."""
    return get_registry().call_metric(metric_id, **kwargs)