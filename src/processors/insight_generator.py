from src.utils.llm_client import LLMClient
from src.state import Article
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

class InsightGenerator:
    def __init__(self):
        self.llm = LLMClient().get_chat_model(temperature=0.3)

    def generate_insight(self, article: Article, summary: str) -> str:
        prompt_text = """
        Based on the following article summary, provide a one-sentence technical insight for an AI Engineer in Korean.
        Explain WHY this is important or how it can be applied in practice.
        
        Example: "기존 RAG의 검색 정확도 한계를 지식 그래프 결합으로 극복할 수 있는 가능성을 보여줌."
        
        Article Title: {title}
        Summary: {summary}
        
        Insight:
        """
        prompt = ChatPromptTemplate.from_template(prompt_text)
        chain = prompt | self.llm | StrOutputParser()
        return chain.invoke({"title": article.title, "summary": summary})
