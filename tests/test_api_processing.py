"""Tests for helper utilities inside cap.api."""

from __future__ import annotations

import json

import pandas as pd
import plotly.graph_objects as go
import pytest

try:
    import polars as pl
except ImportError:  # pragma: no cover - optional dependency
    pl = None

from cap.api import _process_result, _convert_query_params, _generate_html_output


def test_process_result_dataframe():
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    result_type, processed = _process_result(df, output_format="json")
    assert result_type == "dataframe"
    assert processed == df.to_dict(orient="records")

    result_type, processed = _process_result(df, output_format="csv")
    assert result_type == "dataframe"
    assert "a,b" in processed


def test_process_result_plotly_html():
    fig = go.Figure(data=[go.Bar(x=[1], y=[2])])
    result_type, processed = _process_result(fig, output_format="html")
    assert result_type == "plotly"
    assert "<html" in processed.lower()



def test_process_result_polars_dataframe():
    if pl is None:
        pytest.skip("polars not installed")
    df = pl.DataFrame({"a": [1, 2], "b": [3, 4]})
    result_type, processed = _process_result(df, output_format="json")
    assert result_type == "dataframe"
    assert processed == df.to_pandas().to_dict(orient="records")

def test_process_result_mixed_dict():
    df = pd.DataFrame({"value": [1, 2]})
    fig = go.Figure(data=[go.Bar(x=[1], y=[2])])
    result_type, processed = _process_result({"table": df, "chart": fig}, output_format="json")
    assert result_type == "complex"
    assert isinstance(processed["table"], list)
    assert "data" in processed["chart"]


def test_convert_query_params_with_types(monkeypatch):
    class DummyRegistry:
        def get_config(self, metric_id: str):
            assert metric_id == "demo"
            return {
                "inputs": [
                    {"name": "count", "type": "integer"},
                    {"name": "ratio", "type": "float"},
                    {"name": "flag", "type": "boolean"},
                    {"name": "items", "type": "array"},
                    {"name": "payload", "type": "object"},
                ]
            }

    monkeypatch.setattr("cap.api.get_registry", lambda: DummyRegistry())

    params = {
        "count": "5",
        "ratio": "1.25",
        "flag": "true",
        "items": json.dumps([1, 2, 3]),
        "payload": json.dumps({"x": 1}),
    }

    converted = _convert_query_params("demo", params)
    assert converted == {
        "count": 5,
        "ratio": 1.25,
        "flag": True,
        "items": [1, 2, 3],
        "payload": {"x": 1},
    }


def test_generate_html_output_contains_sections(monkeypatch):
    df = pd.DataFrame({"value": [1, 2, 3]})

    class DummyRegistry:
        def get_config(self, metric_id: str):
            assert metric_id == "demo"
            return {
                "name": "Demo",
                "description": "Demo metric",
                "inputs": [],
            }

    monkeypatch.setattr("cap.api.get_registry", lambda: DummyRegistry())

    html = _generate_html_output("demo", df, {"input_data": [1, 2, 3]})
    assert "<html" in html.lower()
    assert "Demo metric" in html
    assert "input_data" in html
