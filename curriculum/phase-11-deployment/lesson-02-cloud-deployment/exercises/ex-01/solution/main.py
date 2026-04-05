"""
Exercise: Deployment Configuration Utilities — Solution
=======================================================
"""

import math


class DeploymentConfig:
    """Generates deployment configuration files for an application."""

    def __init__(self, app_name: str, port: int, env_vars: dict | None = None):
        """Initialize deployment configuration."""
        self.app_name = app_name
        self.port = port
        self.env_vars = env_vars or {}

    def generate_nginx_config(self, domain: str, ssl: bool = False) -> str:
        """Generate an Nginx reverse proxy configuration."""
        listen_port = 443 if ssl else 80
        lines = [
            "server {",
            f"    listen {listen_port}{' ssl' if ssl else ''};",
            f"    server_name {domain};",
            "",
        ]

        if ssl:
            lines.extend([
                f"    ssl_certificate /etc/letsencrypt/live/{domain}/fullchain.pem;",
                f"    ssl_certificate_key /etc/letsencrypt/live/{domain}/privkey.pem;",
                "",
            ])

        lines.extend([
            "    location / {",
            f"        proxy_pass http://127.0.0.1:{self.port};",
            "        proxy_set_header Host $host;",
            "        proxy_set_header X-Real-IP $remote_addr;",
            "    }",
            "}",
        ])

        return "\n".join(lines)

    def generate_systemd_service(self, command: str, user: str = "app", working_dir: str = "/app") -> str:
        """Generate a systemd .service file content."""
        return "\n".join([
            "[Unit]",
            f"Description={self.app_name}",
            "After=network.target",
            "",
            "[Service]",
            "Type=simple",
            f"User={user}",
            f"WorkingDirectory={working_dir}",
            f"ExecStart={command}",
            "Restart=always",
            "RestartSec=5",
            "Environment=PYTHONUNBUFFERED=1",
            "",
            "[Install]",
            "WantedBy=multi-user.target",
        ])

    def generate_env_file(self, env_vars: dict, secrets: list[str] | None = None) -> str:
        """Generate a .env file content."""
        secrets = secrets or []
        lines = []

        for key, value in env_vars.items():
            if key in secrets:
                lines.append(f"# SECRET - do not commit")
            lines.append(f"{key}={value}")

        return "\n".join(lines)

    def generate_health_check_script(self, endpoints: list[str]) -> str:
        """Generate a bash health check script."""
        lines = [
            "#!/bin/bash",
            "# Health check script for " + self.app_name,
            "",
            "EXIT_CODE=0",
            "",
        ]

        for endpoint in endpoints:
            lines.extend([
                f'echo "Checking {endpoint}..."',
                f'STATUS=$(curl -s -o /dev/null -w "%{{http_code}}" --max-time 5 "{endpoint}")',
                'if [ "$STATUS" -eq 200 ]; then',
                f'    echo "  PASS: {endpoint} (HTTP $STATUS)"',
                'else',
                f'    echo "  FAIL: {endpoint} (HTTP $STATUS)"',
                '    EXIT_CODE=1',
                'fi',
                "",
            ])

        lines.extend([
            'if [ "$EXIT_CODE" -eq 0 ]; then',
            '    echo "All health checks passed."',
            'else',
            '    echo "Some health checks failed!"',
            'fi',
            "",
            "exit $EXIT_CODE",
        ])

        return "\n".join(lines)


def estimate_server_requirements(
    model_size_gb: float,
    concurrent_users: int,
    requests_per_second: float,
) -> dict:
    """Estimate server requirements for an AI application."""
    ram_gb = max(4, int(math.ceil(model_size_gb * 2 + concurrent_users * 0.5)))
    cpu_cores = max(2, concurrent_users // 5 + 2)
    gpu_vram_gb = 0 if model_size_gb < 3 else int(math.ceil(model_size_gb * 1.2))
    disk_gb = int(math.ceil(model_size_gb * 3 + 20))

    cost_min = ram_gb * 3 + cpu_cores * 5
    cost_max = int(cost_min * 2.5)

    return {
        "ram_gb": ram_gb,
        "cpu_cores": cpu_cores,
        "gpu_vram_gb": gpu_vram_gb,
        "disk_gb": disk_gb,
        "estimated_monthly_cost_range": {"min": cost_min, "max": cost_max},
    }


# ---------------------------------------------------------------------------
# Do not modify below this line
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    config = DeploymentConfig("my-ai-app", 8000, {"OLLAMA_HOST": "http://localhost:11434"})

    print("=== Nginx Config ===")
    print(config.generate_nginx_config("myapp.example.com"))
    print()

    print("=== Systemd Service ===")
    print(config.generate_systemd_service("python main.py"))
    print()

    print("=== Env File ===")
    print(config.generate_env_file(
        {"API_KEY": "sk-123", "MODEL": "llama2", "DEBUG": "false"},
        secrets=["API_KEY"]
    ))
    print()

    print("=== Health Check Script ===")
    print(config.generate_health_check_script([
        "http://localhost:8000/health",
        "http://localhost:11434/api/tags",
    ]))
    print()

    print("=== Server Requirements ===")
    print(estimate_server_requirements(7.0, 10, 2.0))
