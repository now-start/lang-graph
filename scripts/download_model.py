"""Ollama model download script."""

from __future__ import annotations

import logging
import subprocess
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config.config import Config
logger = logging.getLogger(__name__)


def pull_model() -> None:
    """Download the configured Ollama model."""
    model_id = Config.OLLAMA_MODEL
    logger.info("Pulling Ollama model: %s", model_id)

    try:
        subprocess.run(["ollama", "pull", model_id], check=True)
        logger.info("Model %s pulled successfully.", model_id)
    except subprocess.CalledProcessError as e:
        logger.error("Error pulling model: %s", e)
    except FileNotFoundError:
        logger.error("'ollama' command not found. Please install Ollama first.")


if __name__ == "__main__":
    pull_model()
