"""Utilities that orchestrate fetching and transforming metric input data."""

from __future__ import annotations

from collections import defaultdict
from typing import Callable, Dict, Iterable, Mapping, MutableMapping, Sequence

import pandas as pd

from .sources import BaseSource

import logging

logger = logging.getLogger(__name__)

Transformer = Callable[[pd.DataFrame], pd.DataFrame]


class DataTreatment:
    """Manage sources and transformations that prepare data for metrics."""

    def __init__(
        self,
        sources: Mapping[str, BaseSource] | None = None,
    ) -> None:
        self._sources: Dict[str, BaseSource] = {}
        self._transformers: MutableMapping[str, list[Transformer]] = defaultdict(list)
        if sources:
            for name, source in sources.items():
                self.register_source(name, source)

    def register_source(self, name: str, source: BaseSource) -> None:
        """Attach a ``BaseSource`` to the treatment pipeline under ``name``."""
        if not isinstance(source, BaseSource):
            raise TypeError("source must inherit from BaseSource")
        logger.debug("Registering data source '%s' (%s)", name, source.__class__.__name__)
        self._sources[name] = source

    def add_transformer(self, name: str, transformer: Transformer) -> None:
        """Append a transformation callable that runs after the source fetch."""
        logger.debug("Adding transformer for source '%s': %s", name, transformer)
        self._transformers[name].append(transformer)

    def load(
        self,
        name: str,
        *,
        apply_transformers: bool = True,
        **fetch_kwargs,
    ) -> pd.DataFrame:
        """Retrieve a single source and optionally apply its transformers."""
        if name not in self._sources:
            raise KeyError(f"Unknown data source '{name}'")
        logger.info("Loading data for source '%s'", name)
        df = self._sources[name].fetch(**fetch_kwargs)
        if apply_transformers:
            for transformer in self._transformers.get(name, []):
                df = transformer(df)
        return df

    def load_many(
        self,
        names: Iterable[str] | None = None,
        *,
        fetch_plan: Mapping[str, Mapping[str, object]] | None = None,
        apply_transformers: bool = True,
    ) -> Dict[str, pd.DataFrame]:
        """Retrieve several sources, honoring optional per-source fetch overrides."""
        selected = names or self._sources.keys()
        results: Dict[str, pd.DataFrame] = {}
        for name in selected:
            kwargs = dict(fetch_plan.get(name, {})) if fetch_plan else {}
            results[name] = self.load(
                name,
                apply_transformers=apply_transformers,
                **kwargs,
            )
        return results

    def available_sources(self) -> Sequence[str]:
        """Return a tuple of all registered source names."""
        return tuple(self._sources.keys())
