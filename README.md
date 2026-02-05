# LangGraph RAG Chatbot

Elasticsearch + Ollama 기반 RAG(Retrieval-Augmented Generation) 챗봇

## 특징

- 🤖 **로컬 LLM**: Ollama 기반 (Qwen3:4b)
- 🔍 **벡터 검색**: Elasticsearch + 벡터 임베딩
- 📚 **RAG 지원**: 문서 기반 컨텍스트 검색
- 🐳 **자동 시작**: Docker Compose 자동 실행
- 🔧 **도구 호출**: 날씨 조회, 계산기, 문서 검색
- 📊 **모니터링**: 진행 상황 실시간 표시

## 빠른 시작

### 1. 의존성 설치

```bash
# Python 패키지 설치
uv sync

# 프로젝트 설치 (절대 임포트 지원)
uv pip install -e .
```

### 2. Ollama 모델 다운로드

```bash
# LLM 모델
ollama pull qwen3:4b

# 임베딩 모델
ollama pull qwen3-embedding:0.6b
```

### 3. 문서 임베딩

```bash
# data/ 폴더의 문서를 Elasticsearch에 임베딩
python scripts/embed_documents.py data --pattern "*.docx"

# 또는 Quick Mode (기본 설정)
python scripts/embed_documents.py
```

### 4. LangGraph Dev 서버 실행

```bash
# Elasticsearch가 자동으로 시작됩니다
langgraph dev

# 브라우저에서 자동으로 열림 (http://127.0.0.1:2024)
```

## 환경 설정

`.env` 파일 생성:

```bash
# LLM 모델
OLLAMA_MODEL=qwen3:4b
OLLAMA_BASE_URL=http://localhost:11434

# 임베딩 모델
OLLAMA_EMBEDDING_MODEL=qwen3-embedding:0.6b

# Elasticsearch
ELASTICSEARCH_URL=http://localhost:9200
ELASTICSEARCH_INDEX=documents
```

## 프로젝트 구조

```
.
├── src/
│   ├── graph.py              # 그래프 정의 (Hybrid RAG)
│   ├── config/
│   │   └── config.py         # 환경 설정
│   ├── states/
│   │   └── chatbot.py        # 상태 정의
│   ├── nodes/                # 노드 구현
│   │   ├── model.py          # LLM 호출
│   │   ├── tools_executor.py # 도구 실행
│   │   ├── router.py         # 라우팅
│   │   ├── input_processor.py
│   │   └── retriever.py      # 문서 검색
│   ├── tools/                # 도구 정의
│   │   ├── weather.py
│   │   ├── calculator.py
│   │   └── retriever.py      # Elasticsearch 검색
│   └── utils/
│       ├── llm.py            # LLM 초기화
│       └── docker.py         # Docker 관리
├── scripts/
│   └── embed_documents.py    # 문서 임베딩 스크립트
├── data/                     # 문서 파일
├── docker-compose.yml        # Elasticsearch + Kibana
└── langgraph.json           # LangGraph 설정
```

## RAG 워크플로우

### Hybrid RAG 패턴

```
사용자 입력
    ↓
입력 처리 (process_input)
    ↓
문서 검색 (retrieve) ← 벡터 검색
    ↓
LLM 응답 (agent) ← 검색된 문서 + 사용자 질문
    ↓
도구 호출 필요? ─→ Yes ─→ 도구 실행 (tools) ─┐
    ↓ No                                       │
    ↓ ←─────────────────────────────────────────┘
최종 응답
```

## 문서 임베딩

### 지원 파일 형식

- **DOCX**: Word 문서
- **PDF**: PDF 파일
- **Markdown**: .md, .markdown
- **텍스트**: .txt, .text
- **코드**: .py, .js, .ts, .java, .go

### 임베딩 옵션

```bash
# 기본 사용
python scripts/embed_documents.py <directory>

# 재귀적 검색
python scripts/embed_documents.py <directory> --recursive

# 특정 패턴
python scripts/embed_documents.py <directory> --pattern "*.md"

# 청크 크기 조정
python scripts/embed_documents.py <directory> \
  --chunk-size 500 \
  --chunk-overlap 100

# 배치 크기 조정 (메모리 부족 시)
python scripts/embed_documents.py <directory> --batch-size 10
```

## Docker Services

### Elasticsearch + Kibana

```bash
# 수동 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f elasticsearch

# 중지
docker-compose down

# 데이터 초기화
docker-compose down -v
```
