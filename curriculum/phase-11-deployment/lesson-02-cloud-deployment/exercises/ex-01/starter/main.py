"""
Exercise: Deployment Configuration Utilities
=============================================
Complete the TODOs below.  When you're finished, run the tests:

    pytest ../tests/test_exercise.py

Build utility functions that generate deployment configurations.
"""


class DeploymentConfig:
    """Generates deployment configuration files for an application."""

    def __init__(self, app_name: str, port: int, env_vars: dict | None = None):
        """Initialize deployment configuration.

        Args:
            app_name: Name of the application.
            port: Port the application listens on.
            env_vars: Optional dict of environment variables.
        """
        # TODO: Store app_name, port, and env_vars as instance attributes.
        # Default env_vars to an empty dict if None.
        pass

    def generate_nginx_config(self, domain: str, ssl: bool = False) -> str:
        """Generate an Nginx reverse proxy configuration.

        Args:
            domain: The domain name (e.g., "myapp.example.com").
            ssl: Whether to include SSL configuration.

        Returns:
            An Nginx config string with:
            - server block listening on port 80 (or 443 if ssl)
            - server_name set to domain
            - location / with proxy_pass to http://127.0.0.1:{port}
            - proxy_set_header Host $host
            - proxy_set_header X-Real-IP $remote_addr
            - If ssl: listen 443 ssl, ssl_certificate and ssl_certificate_key paths
        """
        # TODO: Implement this method.
        # Build the nginx config string with proper indentation.
        pass

    def generate_systemd_service(self, command: str, user: str = "app", working_dir: str = "/app") -> str:
        """Generate a systemd .service file content.

        Args:
            command: The command to run the application.
            user: System user to run the service as.
            working_dir: Working directory for the service.

        Returns:
            A systemd service file string with [Unit], [Service], and [Install] sections.
            Should include:
            - Description with app_name
            - After=network.target
            - Type=simple, User, WorkingDirectory, ExecStart
            - Restart=always, RestartSec=5
            - WantedBy=multi-user.target
        """
        # TODO: Implement this method.
        pass

    def generate_env_file(self, env_vars: dict, secrets: list[str] | None = None) -> str:
        """Generate a .env file content.

        Args:
            env_vars: Dict of environment variable names to values.
            secrets: Optional list of variable names that are secrets.
                     Secret values should have a comment: # SECRET - do not commit

        Returns:
            A .env file string with KEY=value lines.
            Secret variables get a comment on the line above.
        """
        # TODO: Implement this method.
        # Loop through env_vars. If the key is in secrets, add a comment line above.
        pass

    def generate_health_check_script(self, endpoints: list[str]) -> str:
        """Generate a bash health check script.

        Args:
            endpoints: List of URL endpoints to check (e.g., ["http://localhost:8000/health"]).

        Returns:
            A bash script string that curls each endpoint and reports status.
            Should include: #!/bin/bash, loop through endpoints, curl with timeout,
            check HTTP status code, print pass/fail for each.
        """
        # TODO: Implement this method.
        pass


def estimate_server_requirements(
    model_size_gb: float,
    concurrent_users: int,
    requests_per_second: float,
) -> dict:
    """Estimate server requirements for an AI application.

    Args:
        model_size_gb: Size of the AI model in gigabytes.
        concurrent_users: Expected number of concurrent users.
        requests_per_second: Expected requests per second.

    Returns:
        A dict with:
            - ram_gb (int): Recommended RAM in GB (model_size * 2 + concurrent_users * 0.5, min 4)
            - cpu_cores (int): Recommended CPU cores (max(2, concurrent_users // 5 + 2))
            - gpu_vram_gb (int): Recommended GPU VRAM (0 if model < 3GB, else model_size * 1.2 rounded up)
            - disk_gb (int): Recommended disk space (model_size * 3 + 20, for model + OS + logs)
            - estimated_monthly_cost_range (dict): {"min": int, "max": int} rough USD estimate
    """
    # TODO: Implement this function.
    # Use the formulas described above to calculate each field.
    # Cost estimate: min = (ram_gb * 3 + cpu_cores * 5), max = min * 2.5
    pass


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
