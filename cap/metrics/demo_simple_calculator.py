"""
Simple Calculator Metric with Rich Outputs

Demonstrates basic mathematical operations with visualization.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from cap import register_metric
from typing import Dict, Any, Sequence
import logging

logger = logging.getLogger(__name__)


@register_metric("demo_simple_calculator")
def calculate_simple_calculator(
    input_data: Sequence[float],
    operation: str = "all"
) -> Dict[str, Any]:
    """
    Simple mathematical calculations with rich outputs.
    
    Args:
        input_data: Primary numeric sequence supplied to the calculator metric
        operation: Type of operation ("all", "sum", "mean", "std")
    
    Returns:
        Dict with calculations table, visualization, and summary
    """
    try:
        if input_data is None:
            raise ValueError("input_data is required")

        try:
            sequence = list(input_data)
        except TypeError as exc:
            raise ValueError("input_data must be an iterable of numeric values") from exc

        logger.info("Calculating with input_data: %s, operation: %s", sequence, operation)

        # Input validation
        if not sequence:
            raise ValueError("Input sequence cannot be empty")

        # Ensure all entries are numeric
        try:
            arr = np.array([float(x) for x in sequence], dtype=float)
        except (TypeError, ValueError) as exc:
            raise ValueError("All input values must be numeric") from exc
        
        # --- CAP USER CODE START ---
        # Perform calculations
        calculations = {
            "sum": float(np.sum(arr)),
            "mean": float(np.mean(arr)),
            "median": float(np.median(arr)),
            "std": float(np.std(arr)),
            "min": float(np.min(arr)),
            "max": float(np.max(arr)),
            "count": len(arr),
        }

        # Create results DataFrame
        results_df = pd.DataFrame(
            {
                "Index": range(len(arr)),
                "Value": arr,
                "Squared": arr**2,
                "Cumulative_Sum": np.cumsum(arr),
            }
        )

        # Create visualization
        fig = go.Figure()

        # Add original values
        fig.add_trace(
            go.Scatter(
                x=results_df["Index"],
                y=results_df["Value"],
                mode="lines+markers",
                name="Original Values",
                line=dict(color="blue", width=3),
            )
        )

        # Add mean line
        fig.add_hline(
            y=calculations["mean"],
            line_dash="dash",
            line_color="red",
            annotation_text=f"Mean: {calculations['mean']:.2f}",
        )

        fig.update_layout(
            title="Number Sequence Analysis",
            xaxis_title="Index",
            yaxis_title="Value",
            template="plotly_white",
            height=400,
        )

        # Create summary based on operation
        allowed_operations = [*sorted(calculations.keys()), "all"]
        if operation == "all":
            summary = calculations
        elif operation in calculations:
            summary = {operation: calculations[operation]}
        else:
            raise ValueError(
                f"Unsupported operation '{operation}'. Choose from {', '.join(allowed_operations)}"
            )

        result = {
            "calculations_table": results_df,
            "visualization": fig,
            "summary_stats": summary,
        }
        # --- CAP USER CODE END ---

        logger.info("Calculation completed successfully")
        return result
        
    except ValueError as e:
        logger.error(f"Calculation failed: {e}")
        raise
    except Exception as e:
        logger.error(f"Calculation failed: {e}")
        raise RuntimeError(f"Calculator metric failed: {e}") from e
