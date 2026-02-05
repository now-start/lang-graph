"""Docker container management utilities."""

import subprocess
import time
from pathlib import Path


def is_docker_running() -> bool:
    """Check if Docker daemon is running.

    Returns:
        True if Docker is available and running
    """
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def is_elasticsearch_running() -> bool:
    """Check if Elasticsearch container is running.

    Returns:
        True if Elasticsearch container is running
    """
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=langgraph-elasticsearch", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return "langgraph-elasticsearch" in result.stdout
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def start_elasticsearch() -> bool:
    """Start Elasticsearch using docker-compose.

    Returns:
        True if started successfully
    """
    project_root = Path(__file__).parent.parent.parent
    compose_file = project_root / "docker-compose.yml"

    if not compose_file.exists():
        print("❌ docker-compose.yml not found")
        return False

    try:
        print("🐳 Starting Elasticsearch containers...")
        result = subprocess.run(
            ["docker-compose", "up", "-d"],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode != 0:
            print(f"❌ Failed to start containers: {result.stderr}")
            return False

        print("⏳ Waiting for Elasticsearch to be healthy...")
        max_retries = 30
        for i in range(max_retries):
            if is_elasticsearch_healthy():
                print("✅ Elasticsearch is ready!")
                print("📊 Kibana available at: http://localhost:5601")
                return True
            time.sleep(2)
            if i % 5 == 0:
                print(f"   Still waiting... ({i}/{max_retries})")

        print("⚠️  Elasticsearch started but health check timed out")
        return True

    except subprocess.TimeoutExpired:
        print("❌ Docker compose command timed out")
        return False
    except FileNotFoundError:
        print("❌ docker-compose command not found. Please install Docker Compose.")
        return False


def is_elasticsearch_healthy() -> bool:
    """Check if Elasticsearch is healthy and responding.

    Returns:
        True if Elasticsearch is healthy
    """
    try:
        import requests
        response = requests.get("http://localhost:9200/_cluster/health", timeout=2)
        return response.status_code == 200
    except Exception:
        return False


def ensure_elasticsearch_running() -> bool:
    """Ensure Elasticsearch is running, start if needed.

    Returns:
        True if Elasticsearch is running or successfully started
    """
    if not is_docker_running():
        print("⚠️  Docker is not running. Please start Docker first.")
        return False

    if is_elasticsearch_running():
        print("✅ Elasticsearch container is already running")
        return True

    print("🚀 Elasticsearch not running, starting automatically...")
    return start_elasticsearch()
