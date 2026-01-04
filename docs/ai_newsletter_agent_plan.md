# 📑 프로젝트명: AI Daily Briefing Agent (Code Name: InsightBot)

## 1. 개요 (Overview)

* **목표:** 전 세계 최신 AI 뉴스, 논문, 기술 블로그를 자동으로 수집하고, LLM을 통해 한국어로 핵심만 요약하여 매일 아침 사용자에게 인사이트를 배달하는 자동화 시스템 구축.
* **핵심 가치:** 정보의 홍수 속에서 "읽어야 할 것"만 선별하여 시간을 절약하고, 단순 번역이 아닌 "기술적 맥락(Insight)"을 제공함.
* **주요 기술:** Python, LangGraph, GPT-4o-mini, GitHub Actions.

## 2. 시스템 아키텍처 (System Architecture)

전체 시스템은 LangGraph를 기반으로 한 **순차적 파이프라인(Pipeline)** 구조를 따릅니다.

### **Phase 1: Collector (정보 수집 에이전트)**

* **역할:** 다양한 소스에서 원문 데이터를 긁어옵니다. (지난 24시간 데이터 한정)
* **Target Sources:**
    * **🔬 논문:**
        * `ArXiv API`: 카테고리 (cs.AI, cs.LG, cs.CL) 필터링.
        * `Hugging Face Daily Papers`: 인기 논문 페이지 크롤링.
    * **📰 기술 블로그 (RSS/Crawling):**
        * Google AI Blog, OpenAI, NVIDIA Blog, Anthropic(Claude), TechCrunch AI, The Verge.
    * **🌐 커뮤니티:**
        * Hacker News (Algolia API 활용 'AI' 키워드 필터링), Reddit (r/MachineLearning).

### **Phase 2: The Brain (지능형 분석 에이전트 - LLM)**

* **엔진:** `gpt-4o-mini` (속도와 비용 효율성 최적화)
* **주요 로직 (LangGraph Node):**
    1. **Filtering Node:** 수집된 데이터의 Title/Abstract를 분석.
        * *기준:* LLM, RAG, Agent, Transformers 등 사용자의 관심 키워드와 연관성 점수(0~1) 채점 후 0.7 미만 탈락.
    2. **Summary Node:** 살아남은 콘텐츠 요약.
        * *논문 프롬프트:* "배경(Problem) - 방법론(Method) - 결과(Result)" 3단 구조로 한글 요약.
        * *뉴스 프롬프트:* 핵심 내용 3줄 요약.
    3. **Insight Node:** 화룡점정.
        * *프롬프트:* "이 소식이 AI 엔지니어에게 중요한 이유를 1문장으로 작성해. (예: 기존 RAG의 한계를 극복함)"

### **Phase 3: Editor (콘텐츠 가공 에이전트)**

* **역할:** JSON 형태의 결과물을 사람이 읽기 좋은 포맷으로 변환.
* **템플릿 구성:**
    * 🔥 **Today's Headline:** 가장 임팩트 있는 뉴스 3건.
    * 📄 **Must-Read Papers:** 핵심 논문 (링크 + 3단 요약 + 인사이트).
    * 🛠️ **Tools & Libraries:** 깃허브 트렌딩 등 실용적인 도구 소개.
* **디자인:** Markdown (슬랙용) / HTML (이메일용, CSS 적용).

### **Phase 4: Publisher (배포 및 자동화)**

* **채널:**
    * 📧 **Email:** SMTP (Gmail) 또는 SendGrid API. (HTML 템플릿 적용)
    * 💬 **Slack:** Incoming Webhook을 통해 지정된 채널에 마크다운 메시지 전송.
* **오디오 (Option):** OpenAI TTS API를 활용하여 "오늘의 헤드라인" 부분만 1분 브리핑 오디오 파일 생성 후 첨부.
* **인프라:** **GitHub Actions**
    * `cron: '0 23 * * *'` (한국 시간 오전 8시에 맞춰 UTC 기준 설정)

---

## 3. 기술 스택 (Tech Stack)

| 구분 | 기술 / 라이브러리 | 선정 이유 |
| --- | --- | --- |
| **Language** | Python 3.10+ | AI 라이브러리 생태계 최적화 |
| **Orchestration** | **LangGraph** | 에이전트 간의 흐름 제어, 상태 관리, 에러 핸들링 용이 |
| **LLM** | **gpt-4o-mini** | 요약 작업에 충분한 성능, 저렴한 비용, 빠른 속도 |
| **Http/Crawling** | `feedparser` (RSS), `requests`, `BeautifulSoup` | 가벼운 데이터 수집 |
| **API** | `arxiv`, `openai`, `slack_sdk` | 전용 라이브러리 활용 |
| **Automation** | **GitHub Actions** | 서버 비용 0원, 스케줄링(Cron) 관리 용이 |

---

## 4. 단계별 개발 로드맵 (Roadmap)

### 📅 Week 1: 핵심 기능 구현 (MVP)

* **Step 1:** `feedparser`와 `arxiv` 라이브러리로 원문 텍스트 긁어오는 파이썬 스크립트 작성.
* **Step 2:** `gpt-4o-mini` API를 연결하여, 긁어온 텍스트 하나를 "배경-방법-결과"로 요약하는 프롬프트 엔지니어링 테스트.
* **Step 3:** LangGraph를 도입하여 `수집 -> 요약` 노드를 연결.

### 📅 Week 2: 포맷팅 및 배포

* **Step 4:** Jinja2 템플릿 등을 사용하여 HTML/Markdown 결과물 생성기 구현.
* **Step 5:** Slack Webhook 및 SMTP 이메일 발송 테스트.
* **Step 6:** GitHub Repository 생성 및 Actions 워크플로우(`main.yml`) 설정.

### 📅 Week 3: 고도화 (Pro)

* **Step 7:** TTS 기능 추가 (OpenAI Audio API).
* **Step 8:** 필터링 정확도 개선 (프롬프트 튜닝).

---

## 5. 예상되는 결과물 예시

> **[2026-01-04] 🧠 Daily AI Briefing**
> **🔥 오늘의 헤드라인**
> * **OpenAI, 새로운 Reasoning 모델 발표:** 기존 o1 모델 대비 추론 속도 2배 향상...
> * *💡 Insight: 실시간 에이전트 서비스 구현이 가능해질 것으로 보임.*
> 
> **📄 주목할 만한 논문**
> * **Title: Self-Correcting LLMs**
> * **배경:** LLM의 환각(Hallucination) 문제 지속.
> * **방법론:** 생성된 답변을 스스로 비평하고 수정하는 2단계 프로세스 도입.
> * **결과:** 기존 모델 대비 정확도 15% 향상.
> * *💡 Insight: RAG 시스템의 신뢰성을 높이는 데 바로 적용 가능한 기법.*
