# LangGraph Sample Project

LangGraph 예제 프로젝트 - Qwen 로컬 모델과 도구 호출

## 특징

- 🤖 Qwen/Qwen2.5-1.5B-Instruct (가볍고 빠른 1.5B 모델)
- 🔧 도구 호출 (날씨 조회, 계산기)
- 🌐 LangGraph Dev 서버 (웹 UI)
- 📊 깔끔한 모듈 구조

## 빠른 시작

```bash
# 의존성 설치
uv sync

# 프로젝트 설치 (절대 임포트 지원)
uv pip install -e .

# LangGraph Dev 서버 실행
langgraph dev

# 브라우저에서 자동으로 열림 (http://127.0.0.1:2024)
```

### 비동기 처리

이 프로젝트는 HuggingFace Transformers의 블로킹 호출을 `asyncio.to_thread()`로 래핑하여 비동기 환경에서 안전하게 실행됩니다.

**참고:** 만약 블로킹 경고가 나타나면:
- 개발 환경: `langgraph dev --allow-blocking`
- 프로덕션: 환경변수 `BG_JOB_ISOLATED_LOOPS=true` 설정

## 프로젝트 구조

```
src/
├── chatbot.py           # 그래프 설정
├── config/              # 설정
│   └── config.py
├── states/              # 상태 정의
│   └── chatbot.py
├── nodes/               # 노드 구현
│   ├── model.py        # LLM 호출
│   ├── tools_executor.py # 도구 실행
│   └── router.py       # 라우팅
├── tools/              # 도구 정의
│   ├── weather.py
│   └── calculator.py
└── utils/              # 유틸리티
    └── llm.py
```

## Chatbot 그래프

Qwen 2.5 모델 기반 대화형 챗봇:
- 자연어 대화 처리
- 도구 호출: 날씨 조회, 계산기
- 대화 히스토리 관리
- 컨텍스트 유지

## 설정

`.env` 파일:

```bash
HUGGINGFACE_MODEL=Qwen/Qwen2.5-1.5B-Instruct
```

다른 모델로 변경 가능:
- `Qwen/Qwen2.5-3B-Instruct` - 3B, 더 높은 품질
- `google/gemma-2-2b-it` - 2B, Google 모델
- `LGAI-EXAONE/EXAONE-3.5-2.4B-Instruct` - 2.4B, 한국어 특화

## 아키텍처

### 관심사의 분리

- **states/**: 데이터 구조 (TypedDict)
- **nodes/**: 비즈니스 로직 (순수 함수)
- **chatbot.py**: 그래프 구조
- **tools/**: 재사용 가능한 도구

이 구조는:
- 그래프 흐름을 한눈에 파악 가능
- 노드와 도구 재사용 용이
- 확장성과 유지보수성 향상

## 확장하기

### 새 도구 추가

1. `src/tools/`에 파일 생성
2. `@tool` 데코레이터 사용
3. `tools/__init__.py`에서 export
4. `nodes/tools_executor.py`에서 등록

### 새 노드 추가

1. `src/nodes/`에 파일 생성
2. 순수 함수로 구현: `(state) -> state`
3. `nodes/__init__.py`에서 export
4. `chatbot.py`에서 연결

상세 문서: [PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md)
