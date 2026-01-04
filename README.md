# 🤖 InsightBot (AI Daily Briefing Agent)

## 📌 개요 (Overview)
**InsightBot**은 전 세계의 최신 AI 뉴스, 논문, 기술 블로그를 자동으로 수집하고, LLM을 활용하여 한국어로 핵심 인사이트를 요약해 제공하는 자동화 에이전트입니다.

### ✨ 주요 기능
- **Data Collection**: ArXiv, RSS Feeds, Tech Blogs에서 지난 24시간 내의 데이터 수집
- **Intelligent Analysis**: GPT-4o-mini를 활용한 관련성 필터링 및 "배경-방법-결과" 3단 요약
- **Insight Extraction**: 엔지니어 관점에서의 기술적 시사점 도출
- **Multi-Channel Publishing**: Slack 및 Email을 통한 브리핑 배포 (Markdown/HTML)

## 🏗 시스템 아키텍처
LangGraph 기반의 순차적 파이프라인으로 구성되어 있습니다.
`Collector` -> `Filter` -> `Summary` -> `Insight` -> `Publisher`

## 🚀 시작하기 (Getting Started)

### 1. 환경 설정
Python 3.10+ 환경이 필요합니다.

```bash
# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate  # Windows

# 의존성 설치
pip install -r requirements.txt
```

### 2. 설정 파일 (Configuration)
`.env` 파일을 생성하고 필수 키를 입력하세요.
```ini
OPENAI_API_KEY=sk-...
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
```

### 3. 실행
```bash
python src/main.py
```

## 📜 License
MIT License
