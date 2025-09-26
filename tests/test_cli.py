"""Tests for cap.scaffolding.cli."""

from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from cap.scaffolding.cli import cli


def test_cli_create_and_generate_workflow():
    runner = CliRunner()
    with runner.isolated_filesystem():
        Path("cap/metrics").mkdir(parents=True)
        Path("cap/__init__.py").write_text("# package marker\n")

        result = runner.invoke(
            cli,
            [
                "create",
                "Sample Metric",
                "--category",
                "demo",
                "--description",
                "Test metric",
                "--template",
                "simple",
            ],
        )
        assert result.exit_code == 0, result.output

        metric_id = "demo_sample_metric"
        assert (Path("cap/metrics") / f"{metric_id}.yaml").exists()
        assert not (Path("cap/metrics") / f"{metric_id}.py").exists()

        # Materialise scaffolding from YAML
        result = runner.invoke(
            cli,
            [
                "generate",
                metric_id,
                "--overwrite-tests",
                "--overwrite-deploy",
            ],
        )
        assert result.exit_code == 0, result.output

        python_path = Path("cap/metrics") / f"{metric_id}.py"
        test_path = Path("tests") / f"test_{metric_id}.py"
        deploy_path = Path("deploy") / f"{metric_id}.py"

        assert python_path.exists()
        assert test_path.exists()
        assert deploy_path.exists()

        contents = python_path.read_text()
        assert "# --- CAP USER CODE START ---" in contents

        customised = contents.replace(
            "# --- CAP USER CODE START ---",
            "# --- CAP USER CODE START ---\n        custom_flag = True",
            1,
        )
        python_path.write_text(customised)

        result = runner.invoke(
            cli,
            [
                "generate",
                metric_id,
                "--overwrite-tests",
                "--overwrite-deploy",
            ],
        )
        assert result.exit_code == 0, result.output
        assert "custom_flag = True" in python_path.read_text()


def test_cli_list_uses_registry(monkeypatch):
    runner = CliRunner()

    class DummyRegistry:
        def list_all(self):
            return [
                {
                    "id": "demo_metric",
                    "name": "Demo Metric",
                    "category": "demo",
                    "description": "Demo description",
                    "inputs": [{"name": "value"}],
                }
            ]

    monkeypatch.setattr("cap.core.get_registry", lambda: DummyRegistry())

    result = runner.invoke(cli, ["list"])
    assert result.exit_code == 0
    assert "demo_metric" in result.output
    assert "Demo Metric" in result.output
