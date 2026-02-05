#!/usr/bin/env python3
"""모델 사전 다운로드 스크립트.

LangGraph dev 서버 시작 전에 HuggingFace 모델을 미리 다운로드합니다.
"""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config.config import Config
from transformers import AutoTokenizer, AutoModelForCausalLM
from tqdm.auto import tqdm


def download_model():
    """HuggingFace 모델 다운로드."""
    model_id = Config.HUGGINGFACE_MODEL

    print("=" * 60)
    print(f"🔄 모델 다운로드 중: {model_id}")
    print("=" * 60)
    print()
    print("첫 다운로드는 시간이 걸릴 수 있습니다 (약 3GB)")
    print("이후에는 캐시된 모델을 사용합니다.")
    print()

    try:
        # Tokenizer 다운로드
        with tqdm(desc="📥 Tokenizer 다운로드 중", unit="B", unit_scale=True) as pbar:
            tokenizer = AutoTokenizer.from_pretrained(
                model_id,
                force_download=False,
                resume_download=True
            )
        print("✓ Tokenizer 다운로드 완료")
        print()

        # Model 다운로드
        with tqdm(desc="📥 Model 다운로드 중", unit="B", unit_scale=True) as pbar:
            model = AutoModelForCausalLM.from_pretrained(
                model_id,
                low_cpu_mem_usage=True,
                force_download=False,
                resume_download=True
            )
        print("✓ Model 다운로드 완료")
        print()

        # 캐시 위치 표시
        cache_dir = Path.home() / ".cache" / "huggingface" / "hub"
        print(f"📁 모델 캐시 위치: {cache_dir}")
        print()

        print("=" * 60)
        print("✅ 모델 다운로드 완료!")
        print("=" * 60)
        print()
        print("이제 다음 명령어로 서버를 실행할 수 있습니다:")
        print("  langgraph dev")
        print()

        return True

    except Exception as e:
        print()
        print("=" * 60)
        print("❌ 모델 다운로드 실패")
        print("=" * 60)
        print(f"오류: {e}")
        print()
        print("문제 해결:")
        print("1. 인터넷 연결 확인")
        print("2. HuggingFace 모델 ID 확인:")
        print(f"   {model_id}")
        print("3. 디스크 공간 확인 (최소 10GB 필요)")
        print()
        return False


if __name__ == "__main__":
    success = download_model()
    sys.exit(0 if success else 1)
