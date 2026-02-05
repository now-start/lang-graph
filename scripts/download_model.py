"""Ollama 모델 풀링 스크립트.

Ollama가 실행 중이어야 합니다.
"""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import subprocess
from src.config.config import Config


def pull_model():
    """Ollama 모델 다운로드."""
    model_id = Config.OLLAMA_MODEL
    print(f"🔄 Pulling Ollama model: {model_id}")
    
    try:
        subprocess.run(["ollama", "pull", model_id], check=True)
        print(f"✅ Model {model_id} pulled successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error pulling model: {e}")
    except FileNotFoundError:
        print("❌ 'ollama' command not found. Please install Ollama first.")


if __name__ == "__main__":
    pull_model()
