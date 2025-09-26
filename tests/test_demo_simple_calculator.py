"""
Tests for demo_simple_calculator metric.

Generated using the cap scaffolding system.
Uses pytest framework exclusively for all testing needs.
"""

import pandas as pd
import pytest
from unittest.mock import patch

from cap.metrics.demo_simple_calculator import calculate_simple_calculator


class TestCalculatesimplecalculator:
    """Test suite for calculate_simple_calculator using pytest."""

    @pytest.fixture
    def sample_inputs(self):
        """Provide sample inputs for testing."""
        df = pd.DataFrame({"value": [1, 2, 3, 4, 5]})
        return {"input_data": df, "operation": "all"}

    def test_basic_calculation(self, sample_inputs):
        """Test basic metric calculation with valid inputs."""
        result = calculate_simple_calculator(**sample_inputs)

        assert isinstance(result, dict)
        assert set(result.keys()) == {"calculations_table", "visualization", "summary_stats"}
        assert "mean" in result["summary_stats"]
        assert round(result["summary_stats"]["sum"], 2) == 15.0

    def test_input_validation(self):
        """Test input validation with pytest.raises."""
        with pytest.raises(ValueError):
            calculate_simple_calculator(input_data=pd.DataFrame(columns=["value"]))

        with pytest.raises(ValueError):
            calculate_simple_calculator(input_data=pd.DataFrame({"value": [1, "a", 3]}))

    @pytest.mark.parametrize(
        "operation,expected",
        [
            ("sum", 6.0),
            ("mean", 2.0),
            ("max", 3.0),
        ],
    )
    def test_operation_filtering(self, operation, expected):
        """Verify that single-operation summaries are respected."""
        df = pd.DataFrame({"value": [1, 2, 3]})
        result = calculate_simple_calculator(input_data=df, operation=operation)
        assert list(result["summary_stats"].keys()) == [operation]
        assert pytest.approx(result["summary_stats"][operation], rel=1e-6) == expected

    def test_invalid_operation(self):
        """Errors if unsupported operation requested."""
        with pytest.raises(ValueError):
            df = pd.DataFrame({"value": [1, 2, 3]})
            calculate_simple_calculator(input_data=df, operation="median_absolute")

    def test_error_handling_and_logging(self):
        """Logs errors before re-raising wrapped exceptions."""
        with patch("cap.metrics.demo_simple_calculator.logger") as mock_logger:
            with pytest.raises(ValueError):
                df = pd.DataFrame({"value": ["x", "y"]})
                calculate_simple_calculator(input_data=df)  # non-numeric
            mock_logger.error.assert_called()

    def test_result_structure(self, sample_inputs):
        """Test that result has expected structure."""
        result = calculate_simple_calculator(**sample_inputs)

        table = result["calculations_table"]
        assert list(table.columns) == ["Index", "Value", "Squared", "Cumulative_Sum"]
        assert len(table) == len(sample_inputs["input_data"])


class TestIntegration:
    """Integration tests with the metrics hub system using pytest."""
    
    def test_metric_registration(self):
        """Test that metric is properly registered."""
        from cap import get_metric
        
        metric_func = get_metric("demo_simple_calculator")
        assert metric_func is not None
        assert metric_func.__name__ == "calculate_simple_calculator"
    
    def test_metric_config_loading(self):
        """Test that metric configuration is loaded correctly."""
        from cap.core import get_registry
        
        registry = get_registry()
        config = registry.get_config("demo_simple_calculator")
        
        assert config is not None
        assert config["id"] == "demo_simple_calculator"
        assert "inputs" in config
        assert "outputs" in config

        # Validate specific configuration elements
        assert {inp["name"] for inp in config["inputs"]} == {"input_data", "operation"}
        assert {out["name"] for out in config["outputs"]} == {
            "calculations_table",
            "visualization",
            "summary_stats",
        }
    
    def test_api_integration(self):
        """Test metric through API interface using FastAPI TestClient."""
        pytest.importorskip("fastapi")  # Skip if FastAPI not available
        
        from cap.api import create_api_app
        pytest.importorskip("httpx")
        from fastapi.testclient import TestClient
        
        app = create_api_app()
        
        with TestClient(app) as client:
            # Test metric listing endpoint
            response = client.get("/metrics")
            assert response.status_code == 200
            
            metrics = response.json()
            metric_ids = [m['id'] for m in metrics]
            assert "demo_simple_calculator" in metric_ids
            
            # Test metric calculation endpoint
            test_payload = {
                "metric_id": "demo_simple_calculator",
                "inputs": {
                    "input_data": [{"value": 1}, {"value": 2}, {"value": 3}],
                    "operation": "sum",
                },
                "output_format": "json",
            }
            
            response = client.post("/calculate", json=test_payload)
            assert response.status_code == 200
            
            result = response.json()
            assert result["success"] is True
            assert result["metric_id"] == "demo_simple_calculator"
            assert result["result_type"] == "complex"
            assert "summary_stats" in result["result"]
    
    @pytest.mark.slow  # Mark for slow tests that can be skipped
    def test_dashboard_integration(self):
        """Test metric integration with dashboard."""
        pytest.importorskip("dash")  # Skip if Dash not available
        
        from cap.dashboard import create_dashboard_app
        
        # Test that dashboard can be created with this metric
        app = create_dashboard_app()
        assert app is not None
        
        # Test that metric appears in dashboard registry
        from cap import list_metrics
        metrics = list_metrics()
        metric_ids = [m['id'] for m in metrics]
        assert "demo_simple_calculator" in metric_ids


# Pytest configuration and fixtures
@pytest.fixture(scope="session")
def test_metric_id():
    """Provide the metric ID for session-wide tests."""
    return "demo_simple_calculator"


@pytest.fixture(scope="session") 
def test_function():
    """Provide the metric function for session-wide tests."""
    return calculate_simple_calculator
