"""Tests for Exercise 1 — Deployment Configuration Utilities."""

import importlib.util
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
def config(mod):
    return mod.DeploymentConfig("test-app", 8000)


# ---------------------------------------------------------------------------
# Tests — DeploymentConfig.__init__
# ---------------------------------------------------------------------------

def test_config_stores_attributes(mod):
    """DeploymentConfig should store app_name, port, and env_vars."""
    cfg = mod.DeploymentConfig("my-app", 3000, {"KEY": "val"})
    assert cfg.app_name == "my-app"
    assert cfg.port == 3000
    assert cfg.env_vars == {"KEY": "val"}


def test_config_default_env_vars(mod):
    """env_vars should default to empty dict."""
    cfg = mod.DeploymentConfig("my-app", 3000)
    assert cfg.env_vars == {}


# ---------------------------------------------------------------------------
# Tests — generate_nginx_config
# ---------------------------------------------------------------------------

def test_nginx_contains_domain(config):
    """Nginx config should contain the domain name."""
    result = config.generate_nginx_config("myapp.example.com")
    assert "myapp.example.com" in result


def test_nginx_contains_proxy_pass(config):
    """Nginx config should proxy to the correct port."""
    result = config.generate_nginx_config("myapp.example.com")
    assert "proxy_pass http://127.0.0.1:8000" in result


def test_nginx_ssl_has_443(config):
    """SSL config should listen on port 443."""
    result = config.generate_nginx_config("myapp.example.com", ssl=True)
    assert "443" in result
    assert "ssl_certificate" in result


# ---------------------------------------------------------------------------
# Tests — generate_systemd_service
# ---------------------------------------------------------------------------

def test_systemd_has_sections(config):
    """Systemd service should have Unit, Service, and Install sections."""
    result = config.generate_systemd_service("python main.py")
    assert "[Unit]" in result
    assert "[Service]" in result
    assert "[Install]" in result


def test_systemd_has_exec_start(config):
    """Systemd service should contain the ExecStart command."""
    result = config.generate_systemd_service("python main.py")
    assert "ExecStart=python main.py" in result


def test_systemd_has_restart(config):
    """Systemd service should have Restart=always."""
    result = config.generate_systemd_service("python main.py")
    assert "Restart=always" in result


# ---------------------------------------------------------------------------
# Tests — generate_env_file
# ---------------------------------------------------------------------------

def test_env_file_contains_vars(config):
    """Env file should contain all variables."""
    result = config.generate_env_file({"MODEL": "llama2", "PORT": "8000"})
    assert "MODEL=llama2" in result
    assert "PORT=8000" in result


def test_env_file_marks_secrets(config):
    """Env file should mark secret variables with a comment."""
    result = config.generate_env_file(
        {"API_KEY": "sk-123", "MODEL": "llama2"},
        secrets=["API_KEY"]
    )
    assert "# SECRET - do not commit" in result
    assert "API_KEY=sk-123" in result


# ---------------------------------------------------------------------------
# Tests — generate_health_check_script
# ---------------------------------------------------------------------------

def test_health_script_has_shebang(config):
    """Health check script should start with #!/bin/bash."""
    result = config.generate_health_check_script(["http://localhost:8000/health"])
    assert result.startswith("#!/bin/bash")


def test_health_script_checks_endpoints(config):
    """Health check script should curl each endpoint."""
    endpoints = ["http://localhost:8000/health", "http://localhost:11434/api/tags"]
    result = config.generate_health_check_script(endpoints)
    for endpoint in endpoints:
        assert endpoint in result


# ---------------------------------------------------------------------------
# Tests — estimate_server_requirements
# ---------------------------------------------------------------------------

def test_estimate_returns_all_keys(mod):
    """Estimate should return all required keys."""
    result = mod.estimate_server_requirements(7.0, 10, 2.0)
    assert "ram_gb" in result
    assert "cpu_cores" in result
    assert "gpu_vram_gb" in result
    assert "disk_gb" in result
    assert "estimated_monthly_cost_range" in result


def test_estimate_minimum_ram(mod):
    """RAM should be at least 4 GB."""
    result = mod.estimate_server_requirements(0.5, 1, 0.1)
    assert result["ram_gb"] >= 4


def test_estimate_gpu_small_model(mod):
    """Models under 3 GB should not require GPU VRAM."""
    result = mod.estimate_server_requirements(2.0, 5, 1.0)
    assert result["gpu_vram_gb"] == 0


def test_estimate_gpu_large_model(mod):
    """Models over 3 GB should require GPU VRAM."""
    result = mod.estimate_server_requirements(7.0, 10, 2.0)
    assert result["gpu_vram_gb"] > 0


def test_estimate_cost_range_sensible(mod):
    """Cost range max should be greater than min."""
    result = mod.estimate_server_requirements(7.0, 10, 2.0)
    cost = result["estimated_monthly_cost_range"]
    assert cost["max"] > cost["min"]
