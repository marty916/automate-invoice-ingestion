from __future__ import annotations

from collections.abc import Callable
from typing import Any


def scenario_pass_rate(signal: Any) -> float:
    if isinstance(signal, (int, float)):
        return float(signal)
    if isinstance(signal, dict):
        passed = float(signal.get("passed", 0))
        total = float(signal.get("total", 0))
        return passed / total if total else 0.0
    return 0.0


def sla_compliance_rate(signal: Any) -> float:
    return float(signal)


def success_rate(signal: Any) -> float:
    return float(signal)


def required_fields_presence_rate(signal: Any) -> float:
    if not isinstance(signal, list) or not signal:
        return 0.0

    required_fields = {"source", "time", "error_type"}
    valid = 0
    for item in signal:
        if isinstance(item, dict) and required_fields.issubset(item.keys()):
            valid += 1
    return valid / len(signal)


def throughput_compliance_rate(signal: Any) -> float:
    return float(signal)


def retention_policy_compliance(signal: Any) -> float:
    return float(signal)


def get_evaluator_registry() -> dict[str, Callable[[Any], float]]:
    return {
        "scenario_pass_rate": scenario_pass_rate,
        "sla_compliance_rate": sla_compliance_rate,
        "success_rate": success_rate,
        "required_fields_presence_rate": required_fields_presence_rate,
        "throughput_compliance_rate": throughput_compliance_rate,
        "retention_policy_compliance": retention_policy_compliance,
    }
