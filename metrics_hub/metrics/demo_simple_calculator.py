"""
Simple Calculator Metric with Rich Outputs

Demonstrates basic mathematical operations with visualization.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from metrics_hub import register_metric
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


@register_metric("demo_simple_calculator")
def calculate_simple_calculator(
    numbers: List[float] = [1, 2, 3, 4, 5],
    operation: str = "all"
) -> Dict[str, Any]:
    """
    Simple mathematical calculations with rich outputs.
    
    Args:
        numbers: List of numbers to perform calculations on
        operation: Type of operation ("all", "sum", "mean", "std")
    
    Returns:
        Dict with calculations table, visualization, and summary
    """
    try:
        logger.info(f"Calculating with numbers: {numbers}, operation: {operation}")
        
        # Input validation
        if not numbers:
            raise ValueError("Numbers list cannot be empty")
        
        # Convert to numpy array for calculations
        arr = np.array(numbers)
        
        # Perform calculations
        calculations = {
            'sum': float(np.sum(arr)),
            'mean': float(np.mean(arr)),
            'median': float(np.median(arr)),
            'std': float(np.std(arr)),
            'min': float(np.min(arr)),
            'max': float(np.max(arr)),
            'count': len(arr)
        }
        
        # Create results DataFrame
        results_df = pd.DataFrame({
            'Index': range(len(numbers)),
            'Value': numbers,
            'Squared': [x**2 for x in numbers],
            'Cumulative_Sum': np.cumsum(numbers)
        })
        
        # Create visualization
        fig = go.Figure()
        
        # Add original values
        fig.add_trace(go.Scatter(
            x=results_df['Index'],
            y=results_df['Value'],
            mode='lines+markers',
            name='Original Values',
            line=dict(color='blue', width=3)
        ))
        
        # Add mean line
        fig.add_hline(
            y=calculations['mean'],
            line_dash="dash",
            line_color="red",
            annotation_text=f"Mean: {calculations['mean']:.2f}"
        )
        
        fig.update_layout(
            title='Number Sequence Analysis',
            xaxis_title='Index',
            yaxis_title='Value',
            template='plotly_white',
            height=400
        )
        
        # Create summary based on operation
        if operation == "all":
            summary = calculations
        else:
            summary = {operation: calculations.get(operation, "Invalid operation")}
        
        result = {
            'calculations_table': results_df,
            'visualization': fig,
            'summary_stats': summary
        }
        
        logger.info("Calculation completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"Calculation failed: {e}")
        raise RuntimeError(f"Calculator metric failed: {e}") from e