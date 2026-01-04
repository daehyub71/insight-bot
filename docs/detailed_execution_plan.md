# 📋 InsightBot 상세 Task 수행 계획 (Detailed Execution Plan)

이 문서는 `ai_newsletter_agent_plan.md`의 목표를 달성하기 위한 구체적인 작업 단위(Action Items)를 정의합니다. 개발 진행 시 이 문서를 체크리스트로 활용하세요.

## 🛠 0. 프로젝트 초기화 (Environment & Setup)
- [x] **Git Repository 초기화**
    - [x] `.gitignore` 설정 (Python, venv, .env, .DS_Store 등)
    - [x] `README.md` 작성 (프로젝트 개요 및 실행 방법)
- [x] **개발 환경 구성**
    - [x] Python 3.10+ 가상환경 생성 (`python -m venv venv` 또는 `poetry init`)
    - [x] 필수 라이브러리 설치 (`langgraph`, `langchain-openai`, `feedparser`, `arxiv`, `beautifulsoup4`, `python-dotenv`)
    - [x] `requirements.txt` 생성
- [x] **설정 관리**
    - [x] `.env` 파일 생성 (API Key 관리: `OPENAI_API_KEY`, `SLACK_WEBHOOK_URL` 등)
    - [x] `config/settings.yaml` 생성 (수집 대상 URL, 검색 키워드, 필터링 임계값 등 설정)
- [x] **디렉토리 구조 생성**
    - [x] `src/`, `tests/`, `config/`, `templates/`, `.github/workflows/` 등 기본 폴더 구조 생성

## 📡 1. 정보 수집 에이전트 구현 (Phase 1: Collector)
*목표: 다양한 소스로부터 지난 24시간 내의 Raw Data를 수집하여 리스트 형태로 반환*

- [ ] **기본 수집 모듈 구조 잡기** (`src/collectors/base.py`)
- [ ] **ArXiv 수집기 개발** (`src/collectors/arxiv_collector.py`)
    - [ ] `arxiv` API 연동
    - [ ] 카테고리(cs.AI, cs.LG) 및 날짜 필터링 로직 구현
    - [ ] 메타데이터 추출 (제목, 요약, 저자, PDF 링크)
- [ ] **RSS/블로그 수집기 개발** (`src/collectors/rss_crawler.py`)
    - [ ] `feedparser` 활용 RSS 파싱 구현
    - [ ] `settings.yaml`의 URL 리스트 순회 로직
    - [ ] 날짜 필터링 (최근 24시간)
- [ ] **단위 테스트 작성** (`tests/test_collectors.py`)
    - [ ] 각 수집기가 정상적으로 데이터를 반환하는지 테스트

## 🧠 2. 지능형 분석 엔진 구현 (Phase 2: The Brain)
*목표: 수집된 데이터의 가치를 판단하고 핵심 내용을 요약/분석*

- [ ] **LLM 유틸리티 구현** (`src/utils/llm_client.py`)
    - [ ] OpenAI API Wrapper 클래스 작성 (모델: `gpt-4o-mini`)
- [ ] **필터링 노드 구현** (`src/processors/filters.py`)
    - [ ] Relevance Scoring 프롬프트 작성 ("이 글이 AI 엔지니어에게 유용한가?")
    - [ ] 점수 파싱 및 Threshold(0.7) 필터링 로직
- [ ] **요약 노드 구현** (`src/processors/summarizer.py`)
    - [ ] **Paper Summary Prompt**: 배경(Problem)-방법(Method)-결과(Result) 3단 구조
    - [ ] **News Summary Prompt**: 핵심 내용 3줄 요약
- [ ] **인사이트 노드 구현** (`src/processors/insight_generator.py`)
    - [ ] **Insight Prompt**: 기술적 시사점 한 문장 추출 로직

## 🔗 3. LangGraph 워크플로우 통합 (Orchestration)
*목표: 수집-필터링-요약-분석의 흐름을 제어하는 그래프 구축*

- [ ] **상태(State) 정의** (`src/state.py`)
    - [ ] `AgentState` TypedDict 정의 (articles list, processing_status 등)
    - [ ] `Article` 데이터 클래스 정의
- [ ] **Graph 구성** (`src/graph.py`)
    - [ ] Node 정의: `fetch_data`, `filter_data`, `summarize_data`
    - [ ] Edge 연결: 순차적 흐름 구성
    - [ ] Conditional Edge: 데이터가 없을 경우 조기 종료 처리
- [ ] **메인 실행부 작성** (`src/main.py`)
    - [ ] 그래프 컴파일 및 실행 (`app.invoke`) 트리거

## 🎨 4. 콘텐츠 가공 및 편집 (Phase 3: Editor)
*목표: JSON 데이터를 사람이 읽기 좋은 포맷으로 변환*

- [ ] **Jinja2 템플릿 환경 설정**
- [ ] **이메일 템플릿 디자인** (`templates/email_template.html`)
    - [ ] Header/Body/Footer 레이아웃
    - [ ] CSS 인라인 스타일링 (이메일 클라이언트 호환성 고려)
- [ ] **슬랙 메시지 빌더 구현** (`src/publishers/slack_builder.py`)
    - [ ] Markdown 포맷 변환 로직 (Bold, Link, Quote 활용)

## 🚀 5. 배포 및 자동화 (Phase 4: Publisher & Pipeline)
*목표: 최종 결과물을 사용자에게 전달하고 이를 매일 자동 실행*

- [ ] **이메일 발송 모듈** (`src/publishers/email_sender.py`)
    - [ ] SMTP (Gmail) 또는 SendGrid API 연동
- [ ] **슬랙 봇 연동** (`src/publishers/slack_bot.py`)
    - [ ] `requests`를 이용한 Incoming Webhook 전송
- [ ] **GitHub Actions 워크플로우** (`.github/workflows/daily_briefing.yml`)
    - [ ] Schedule Trigger 설정 (`cron: '0 23 * * *'`)
    - [ ] Secrets 연동 (Github Settings -> Secrets)
    - [ ] 실행 로그 저장 (Artifacts 활용)

## 🌟 6. 고도화 (Optimization - Week 3)
- [ ] **TTS 브리핑 기능**
    - [ ] OpenAI TTS API 연동 ('오늘의 헤드라인' 텍스트 -> MP3)
    - [ ] 슬랙/이메일에 오디오 파일 첨부 로직
- [ ] **오류 처리 및 로깅 강화**
    - [ ] 수집 실패 시 재시도 로직 (Retry Policy)
    - [ ] `src/utils/logger.py` 구현
