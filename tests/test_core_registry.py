"""Unit tests for cap.core.MetricRegistry."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest

from cap.core import MetricRegistry, register_metric, get_registry


def _create_metrics_package(tmp_path: Path, name: str, files: dict[str, str]) -> str:
    package_path = tmp_path / name.replace('.', '/')
    package_path.mkdir(parents=True)
    (package_path / "__init__.py").write_text("# auto-generated test package\n")
    for filename, content in files.items():
        (package_path / filename).write_text(content)
    sys.modules.pop(name, None)
    if str(tmp_path) not in sys.path:
        sys.path.insert(0, str(tmp_path))
    importlib.invalidate_caches()
    return name


def test_registry_discovers_metrics(tmp_path):
    module_name = _create_metrics_package(
        tmp_path,
        "cap_test_pkg",
        {
            "demo.py": (
                "from cap import register_metric\n\n"
                "@register_metric(\"demo_metric\")\n"
                "def calculate_demo()->int:\n"
                "    return 42\n"
            ),
            "demo.yaml": (
                "id: demo_metric\n"
                "name: Demo Metric\n"
                "description: Demo metric description\n"
                "category: demo\n"
                "inputs: []\n"
                "outputs: []\n"
            ),
        },
    )

    registry = MetricRegistry(metrics_module=module_name)
    metrics = {m["id"] for m in registry.list_all()}
    assert "demo_metric" in metrics
    assert registry.call_metric("demo_metric") == 42
    sys.modules.pop(module_name, None)


def test_register_metric_decorator():
    @register_metric("test_metric_decorator")
    def foo():
        return "ok"

    assert getattr(foo, "__metric_id__") == "test_metric_decorator"


def test_registry_missing_metric():
    registry = MetricRegistry()
    with pytest.raises(ValueError):
        registry.call_metric("missing_metric")


@pytest.mark.parametrize("default", [None, "test", 1])
def test_registry_applies_yaml_defaults(tmp_path, default):
    default_line = "" if default is None else f"    default: {default}\n"

    module_name = _create_metrics_package(
        tmp_path,
        "cap_test_defaults",
        {
            "demo_default.py": (
                "from cap import register_metric\n\n"
                "@register_metric(\"demo_defaults\")\n"
                "def calculate_demo_defaults(param=None):\n"
                "    return param\n"
            ),
            "demo_default.yaml": (
                "id: demo_defaults\n"
                "name: Demo Defaults\n"
                "description: Demo defaults description\n"
                "category: demo\n"
                "inputs:\n"
                "  - name: param\n"
                "    type: string\n"
                "    required: false\n"
                f"{default_line}"
                "outputs: []\n"
            ),
        },
    )

    registry = MetricRegistry(metrics_module=module_name)
    assert registry.call_metric("demo_defaults") == default
    sys.modules.pop(module_name, None)
