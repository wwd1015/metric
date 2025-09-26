"""Tests for the data treatment utilities."""

from __future__ import annotations

import importlib.util

import pandas as pd
import pytest

from cap.data import CSVSource, DataTreatment, ParquetSource, SQLAlchemySource


def test_csv_source_with_transformer(tmp_path):
    df = pd.DataFrame({"country": ["US", "FR", "US"], "value": [10, 20, 30]})
    csv_path = tmp_path / "data.csv"
    df.to_csv(csv_path, index=False)

    source = CSVSource(path=csv_path)
    treatment = DataTreatment({"sales": source})

    def only_us(data: pd.DataFrame) -> pd.DataFrame:
        return data[data["country"] == "US"]

    treatment.add_transformer("sales", only_us)

    result = treatment.load("sales")
    assert list(result["country"]) == ["US", "US"]
    assert result["value"].sum() == 40


@pytest.mark.skipif(importlib.util.find_spec('polars') is None, reason='polars not installed')
def test_csv_source_polars_backend(tmp_path):
    import polars as pl

    df = pl.DataFrame({'country': ['US', 'FR', 'US'], 'value': [10, 20, 30]})
    csv_path = tmp_path / 'data.csv'
    df.write_csv(csv_path)

    from cap.data import CSVSource, DataTreatment

    source = CSVSource(path=csv_path, backend='polars')
    treatment = DataTreatment({'sales': source})
    result = treatment.load('sales')

    assert isinstance(result, pl.DataFrame)
    assert result.filter(pl.col('country') == 'US').shape[0] == 2


def test_parquet_source_reads_when_dependency_available(tmp_path, monkeypatch):
    source = ParquetSource(path=tmp_path / "data.parquet")

    mock_df = pd.DataFrame({"a": [1, 2, 3]})

    def fake_read_parquet(path, **kwargs):  # noqa: D401
        return mock_df

    monkeypatch.setattr(pd, "read_parquet", fake_read_parquet)

    treatment = DataTreatment({"parquet": source})
    result = treatment.load("parquet")
    pd.testing.assert_frame_equal(result, mock_df)


def test_sqlalchemy_source_requires_dependency(monkeypatch):
    real_import = __import__

    def fake_import(name, *args, **kwargs):
        if name == "sqlalchemy":
            raise ImportError("No module named 'sqlalchemy'")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", fake_import)

    source = SQLAlchemySource(connection_string="sqlite://", query="SELECT 1")
    with pytest.raises(ImportError):
        source.fetch()


def test_load_many_with_plan(tmp_path, monkeypatch):
    df_full = pd.DataFrame({"category": ["A", "B"], "value": [1, 2]})
    csv_path = tmp_path / "data.csv"
    df_full.to_csv(csv_path, index=False)

    source = CSVSource(path=csv_path)
    treatment = DataTreatment({"inventory": source})

    result = treatment.load_many(fetch_plan={"inventory": {"columns": ["category"]}})
    assert "inventory" in result
    assert list(result["inventory"].columns) == ["category"]
