# 프로젝트 구조

## 디렉토리 구조

```
lang-graph/
├── src/
│   ├── chatbot.py              # 그래프 설정
│   │
│   ├── config/
│   │   └── config.py          # 환경 설정
│   │
│   ├── states/
│   │   └── chatbot.py         # ChatbotState 정의
│   │
│   ├── nodes/                  # 노드 구현
│   │   ├── model.py           # LLM 호출
│   │   ├── tools_executor.py  # 도구 실행
│   │   └── router.py          # 라우팅 로직
│   │
│   ├── tools/                  # 도구 정의
│   │   ├── weather.py
│   │   └── calculator.py
│   │
│   └── utils/                  # 유틸리티
│       └── llm.py             # LLM 초기화
│
├── langgraph.json             # LangGraph Dev 설정
├── pyproject.toml             # 의존성
├── .env                       # 환경 변수
└── README.md
```

## 아키텍처 원칙

### 1. 관심사의 분리

**states/** - 데이터 구조
```python
class ChatbotState(TypedDict):
    messages: Annotated[list, operator.add]
```

**nodes/** - 비즈니스 로직
```python
def call_model(state: ChatbotState, llm_with_tools) -> ChatbotState:
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}
```

**chatbot.py** - 그래프 구조
```python
workflow = StateGraph(ChatbotState)
workflow.add_node("agent", call_model)
workflow.add_node("tools", call_tools)
workflow.add_conditional_edges("agent", should_continue, {...})
```

**tools/** - 도구 정의
```python
@tool
def get_weather(location: str) -> str:
    """Get weather for a location."""
    return weather_data[location]
```

### 2. 장점

1. **명확성**: 각 디렉토리의 역할이 명확
2. **재사용성**: 노드와 도구를 다른 그래프에서도 사용 가능
3. **테스트 용이**: 각 컴포넌트를 독립적으로 테스트
4. **확장성**: 새 노드/도구 추가가 간단

## Import 패턴

```python
# 그래프 파일 (chatbot.py)
from .states import ChatbotState
from .nodes import call_model, call_tools, should_continue
from .tools import get_weather, calculate
from .utils import get_local_llm

# 노드 파일 (nodes/model.py)
from ..states import ChatbotState

# 도구 실행 노드 (nodes/tools_executor.py)
from ..states import ChatbotState
from ..tools import get_weather, calculate
```

## 그래프 흐름

```
입력 메시지
    ↓
[agent] LLM 호출
    ↓
[조건부 분기]
    ├─ 도구 호출 필요? → [tools] 도구 실행 → [agent]로 돌아감
    └─ 응답 완료? → [end] 종료
```

## 확장 가이드

### 새 도구 추가

1. `src/tools/my_tool.py` 생성:
```python
from langchain_core.tools import tool

@tool
def my_tool(param: str) -> str:
    """도구 설명."""
    return result
```

2. `tools/__init__.py`에서 export:
```python
from .my_tool import my_tool
__all__ = [..., "my_tool"]
```

3. `nodes/tools_executor.py`에서 등록:
```python
from ..tools import get_weather, calculate, my_tool

# call_tools 함수에서
if tool_name == "my_tool":
    result = my_tool.invoke(tool_args)
```

4. `chatbot.py`에서 바인딩:
```python
tools = [get_weather, calculate, my_tool]
```

### 새 노드 추가

1. `src/nodes/my_node.py` 생성:
```python
from ..states import ChatbotState

def my_node(state: ChatbotState) -> ChatbotState:
    # 로직 구현
    return {"messages": [...]}
```

2. `nodes/__init__.py`에서 export:
```python
from .my_node import my_node
__all__ = [..., "my_node"]
```

3. `chatbot.py`에서 연결:
```python
from .nodes import call_model, call_tools, should_continue, my_node

workflow.add_node("my_node", my_node)
workflow.add_edge("some_node", "my_node")
```

## 디자인 철학

> "명확한 구조, 간단한 확장"

- **chatbot.py**: 그래프 구조만
- **nodes/**: 비즈니스 로직만
- **tools/**: 도구 정의만
- **states/**: 데이터 계약만

각 레이어가 독립적이라 쉽게 이해하고 수정할 수 있습니다.
