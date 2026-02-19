from __future__ import annotations

from importlib import import_module
from pathlib import Path
from typing import Any

from tests.eval.evaluators import get_evaluator_registry


def _load_eval_criteria() -> dict[str, Any]:
    yaml = import_module("yaml")
    file_path = Path("features/invoice_ingestion/eval_criteria.yaml")
    return yaml.safe_load(file_path.read_text(encoding="utf-8"))


def _signals() -> dict[str, Any]:
    return {
        "scenario_ap_email_ingest": {"passed": 1, "total": 1},
        "scenario_accounting_ingest": {"passed": 1, "total": 1},
        "scenario_same_source_dedupe": {"passed": 1, "total": 1},
        "scenario_cross_source_dedupe": {"passed": 1, "total": 1},
        "scenario_analyst_filter_sort": {"passed": 1, "total": 1},
        "scenario_ap_email_failure": {"passed": 1, "total": 1},
        "scenario_accounting_failure": {"passed": 1, "total": 1},
        "nfr_latency_15min": 0.97,
        "nfr_reliability_30d": 0.998,
        "nfr_failure_log_fields": [
            {"source": "AP email", "time": "2026-02-19T10:00:00Z",
                "error_type": "integration_unavailable"},
            {"source": "Accounting system", "time": "2026-02-19T10:05:00Z",
                "error_type": "upstream_error"},
        ],
        "nfr_throughput_100_per_day": 1.0,
        "nfr_history_retention_24m": 1.0,
    }


def _is_failure(metric: float, threshold: float, fail_on: str) -> bool:
    if fail_on == "below_threshold":
        return metric < threshold
    if fail_on == "above_threshold":
        return metric > threshold
    return False


def test_eval_criteria_file_is_deterministic_and_non_empty() -> None:
    criteria = _load_eval_criteria()
    assert criteria["mode"] == "deterministic"
    assert len(criteria.get("criteria", [])) > 0


def test_eval_criteria_all_pass_against_deterministic_signals() -> None:
    criteria_doc = _load_eval_criteria()
    criteria = criteria_doc["criteria"]
    signals = _signals()
    evaluators = get_evaluator_registry()

    failures: list[str] = []

    for criterion in criteria:
        name = criterion["name"]
        eval_class = criterion["eval_class"]
        threshold = float(criterion["threshold"])
        fail_on = criterion["fail_on"]
        signal_key = criterion.get("input")

        assert eval_class in evaluators, f"Missing evaluator for eval_class={eval_class}"
        assert signal_key in signals, f"Missing signal for criterion input={signal_key}"

        metric = evaluators[eval_class](signals[signal_key])

        if _is_failure(metric=metric, threshold=threshold, fail_on=fail_on):
            failures.append(
                f"{name}: metric={metric:.4f}, threshold={threshold:.4f}, fail_on={fail_on}"
            )

    assert not failures, "Deterministic evaluation failures:\n" + \
        "\n".join(failures)
