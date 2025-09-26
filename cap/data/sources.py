"""Data source connectors used by the Commercial Analytical Platform (CAP) data treatment layer."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Optional

import pandas as pd

try:  # Optional dependency
    import polars as pl
except ImportError:  # pragma: no cover - optional dependency
    pl = None

import logging

logger = logging.getLogger(__name__)


class BaseSource(ABC):
    """Abstract interface for data sources that produce tabular data."""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def fetch(self, **kwargs) -> pd.DataFrame:
        """Return a DataFrame representing the source data."""


@dataclass
class CSVSource(BaseSource):
    """Read data from a local CSV/TSV file."""

    path: Path | str
    read_kwargs: Dict[str, Any] = field(default_factory=dict)
    backend: str = "pandas"

    def __post_init__(self) -> None:
        super().__init__(name=str(self.path))
        self.path = Path(self.path)

    def fetch(
        self,
        *,
        columns: Optional[Iterable[str]] = None,
        filters: Optional[Mapping[str, Any]] = None,
        **overrides: Any,
    ) -> pd.DataFrame:
        backend = self.backend.lower()
        options = {**self.read_kwargs, **overrides}
        logger.debug("Reading CSV file %s with options %s (backend=%s)", self.path, options, backend)

        if backend == "polars":
            if pl is None:
                raise ImportError(
                    "Polars backend requested but 'polars' is not installed. Install with 'pip install polars'."
                )
            df = pl.read_csv(self.path, **options)
            if columns:
                df = df.select(list(columns))
            if filters:
                for column, expected in filters.items():
                    if isinstance(expected, Iterable) and not isinstance(expected, (str, bytes)):
                        df = df.filter(pl.col(column).is_in(list(expected)))
                    else:
                        df = df.filter(pl.col(column) == expected)
            return df

        df = pd.read_csv(self.path, **options)
        if columns:
            df = df.loc[:, list(columns)]
        if filters:
            for column, expected in filters.items():
                if isinstance(expected, Iterable) and not isinstance(expected, (str, bytes)):
                    df = df[df[column].isin(expected)]
                else:
                    df = df[df[column] == expected]
        return df


@dataclass
class ParquetSource(BaseSource):
    """Read data from a Parquet file."""

    path: Path | str
    read_kwargs: Dict[str, Any] = field(default_factory=dict)
    backend: str = "pandas"

    def __post_init__(self) -> None:
        super().__init__(name=str(self.path))
        self.path = Path(self.path)

    def fetch(
        self,
        *,
        columns: Optional[Iterable[str]] = None,
        filters: Optional[Mapping[str, Any]] = None,
        **overrides: Any,
    ) -> pd.DataFrame:
        backend = self.backend.lower()
        options = {**self.read_kwargs, **overrides}
        logger.debug("Reading Parquet file %s with options %s (backend=%s)", self.path, options, backend)

        if backend == "polars":
            if pl is None:
                raise ImportError(
                    "Polars backend requested but 'polars' is not installed. Install with 'pip install polars'."
                )
            df = pl.read_parquet(self.path, **options)
            if columns:
                df = df.select(list(columns))
            if filters:
                for column, expected in filters.items():
                    if isinstance(expected, Iterable) and not isinstance(expected, (str, bytes)):
                        df = df.filter(pl.col(column).is_in(list(expected)))
                    else:
                        df = df.filter(pl.col(column) == expected)
            return df

        try:
            df = pd.read_parquet(self.path, **options)
        except ImportError as exc:  # pragma: no cover - depends on pyarrow/fastparquet
            raise ImportError(
                "Parquet support requires either 'pyarrow' or 'fastparquet' to be installed"
            ) from exc
        if columns:
            df = df.loc[:, list(columns)]
        if filters:
            for column, expected in filters.items():
                if isinstance(expected, Iterable) and not isinstance(expected, (str, bytes)):
                    df = df[df[column].isin(expected)]
                else:
                    df = df[df[column] == expected]
        return df


@dataclass
class SQLAlchemySource(BaseSource):
    """Execute a SQL query using SQLAlchemy and return the results as a DataFrame."""

    connection_string: str
    query: str
    default_params: Optional[Mapping[str, Any]] = None
    connect_args: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        super().__init__(name=self.connection_string)

    def fetch(self, *, params: Optional[Mapping[str, Any]] = None) -> pd.DataFrame:
        try:
            import sqlalchemy as sa
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise ImportError(
                "SQLAlchemy is required for SQLAlchemySource. Install with 'pip install sqlalchemy'."
            ) from exc

        effective_params = dict(self.default_params or {})
        if params:
            effective_params.update(params)

        logger.debug(
            "Executing SQL query against %s with params %s", self.connection_string, effective_params
        )

        engine = sa.create_engine(self.connection_string, connect_args=self.connect_args)
        try:
            with engine.connect() as conn:
                statement = sa.text(self.query)
                df = pd.read_sql_query(statement, conn, params=effective_params)
        finally:
            engine.dispose()
        return df
