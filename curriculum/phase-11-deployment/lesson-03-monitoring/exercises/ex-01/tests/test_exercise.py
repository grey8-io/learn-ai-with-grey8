"""Tests for Exercise 1 — Monitoring & Observability System."""

import importlib.util
import json
import os
import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SOLUTION_PATH = os.path.join(
    os.path.dirname(__file__), "..", "solution", "main.py"
)


def _load_module(path: str):
    """Import main.py as a module from the given path."""
    spec = importlib.util.spec_from_file_location("student_main", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def mod():
    return _load_module(SOLUTION_PATH)


@pytest.fixture
def metrics(mod):
    m = mod.AIMetrics()
    m.record_request("/chat", 1200, 150, 89, 200, "llama2")
    m.record_request("/chat", 800, 100, 50, 200, "llama2")
    m.record_request("/search", 300, 50, 20, 200, "mistral")
    m.record_request("/chat", 5000, 200, 150, 500, "llama2")
    return m


# ---------------------------------------------------------------------------
# Tests — AIMetrics.record_request
# ---------------------------------------------------------------------------

def test_record_request_stores_data(mod):
    """Recording a request should add to the records list."""
    m = mod.AIMetrics()
    m.record_request("/test", 100, 10, 5, 200)
    assert len(m.records) == 1
    assert m.records[0]["endpoint"] == "/test"


# ---------------------------------------------------------------------------
# Tests — AIMetrics.get_summary
# ---------------------------------------------------------------------------

def test_summary_total_requests(metrics):
    """Summary should count total requests."""
    summary = metrics.get_summary()
    assert summary["total_requests"] == 4


def test_summary_avg_latency(metrics):
    """Summary should calculate average latency."""
    summary = metrics.get_summary()
    expected = round((1200 + 800 + 300 + 5000) / 4, 2)
    assert summary["avg_latency_ms"] == expected


def test_summary_error_rate(metrics):
    """Summary should calculate error rate correctly."""
    summary = metrics.get_summary()
    assert summary["error_rate"] == round(1 / 4, 4)


def test_summary_total_tokens(metrics):
    """Summary should sum all tokens."""
    summary = metrics.get_summary()
    expected = (150 + 89) + (100 + 50) + (50 + 20) + (200 + 150)
    assert summary["total_tokens"] == expected


def test_summary_empty_metrics(mod):
    """Summary of empty metrics should return zeros."""
    m = mod.AIMetrics()
    summary = m.get_summary()
    assert summary["total_requests"] == 0
    assert summary["avg_latency_ms"] == 0.0


# ---------------------------------------------------------------------------
# Tests — AIMetrics.get_model_metrics
# ---------------------------------------------------------------------------

def test_model_metrics_filters_by_model(metrics):
    """Model metrics should only include the specified model."""
    result = metrics.get_model_metrics("llama2")
    assert result["model"] == "llama2"
    assert result["total_requests"] == 3


def test_model_metrics_unknown_model(metrics):
    """Unknown model should return zero counts."""
    result = metrics.get_model_metrics("unknown")
    assert result["total_requests"] == 0


# ---------------------------------------------------------------------------
# Tests — AIMetrics.get_alerts
# ---------------------------------------------------------------------------

def test_alerts_triggered(metrics):
    """Alerts should fire when thresholds are exceeded."""
    rules = [
        {"metric": "error_rate", "operator": ">", "threshold": 0.1, "message": "High errors"},
    ]
    alerts = metrics.get_alerts(rules)
    assert len(alerts) == 1
    assert alerts[0]["message"] == "High errors"


def test_alerts_not_triggered(metrics):
    """Alerts should not fire when thresholds are not exceeded."""
    rules = [
        {"metric": "error_rate", "operator": ">", "threshold": 0.9, "message": "Very high errors"},
    ]
    alerts = metrics.get_alerts(rules)
    assert len(alerts) == 0


# ---------------------------------------------------------------------------
# Tests — StructuredLogger
# ---------------------------------------------------------------------------

def test_log_returns_valid_json(mod):
    """Log output should be valid JSON."""
    logger = mod.StructuredLogger("test-service")
    line = logger.log("info", "test message", key="value")
    parsed = json.loads(line)
    assert parsed["service"] == "test-service"
    assert parsed["level"] == "info"
    assert parsed["message"] == "test message"
    assert parsed["key"] == "value"


def test_log_request_includes_fields(mod):
    """Request log should include method, path, status, and latency."""
    logger = mod.StructuredLogger("api")
    line = logger.log_request("POST", "/chat", 200, 1200)
    parsed = json.loads(line)
    assert parsed["method"] == "POST"
    assert parsed["path"] == "/chat"
    assert parsed["status"] == 200
    assert parsed["latency_ms"] == 1200


def test_log_llm_call_success(mod):
    """Successful LLM call should log at info level."""
    logger = mod.StructuredLogger("api")
    line = logger.log_llm_call("llama2", 150, 89, 1200, True)
    parsed = json.loads(line)
    assert parsed["level"] == "info"
    assert parsed["model"] == "llama2"
    assert parsed["success"] is True


def test_log_llm_call_failure(mod):
    """Failed LLM call should log at error level."""
    logger = mod.StructuredLogger("api")
    line = logger.log_llm_call("llama2", 150, 0, 5000, False)
    parsed = json.loads(line)
    assert parsed["level"] == "error"
    assert parsed["success"] is False


# ---------------------------------------------------------------------------
# Tests — create_dashboard_data
# ---------------------------------------------------------------------------

def test_dashboard_has_all_sections(mod, metrics):
    """Dashboard data should have all required sections."""
    result = mod.create_dashboard_data(metrics)
    assert "requests_chart" in result
    assert "latency_chart" in result
    assert "error_chart" in result
    assert "top_endpoints" in result


def test_dashboard_top_endpoints(mod, metrics):
    """Top endpoints should be sorted by count."""
    result = mod.create_dashboard_data(metrics)
    top = result["top_endpoints"]
    assert len(top) >= 1
    assert top[0]["endpoint"] == "/chat"
    assert top[0]["count"] == 3
