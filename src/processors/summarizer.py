from src.utils.llm_client import LLMClient
from src.state import Article
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

class Summarizer:
    def __init__(self):
        self.llm = LLMClient().get_chat_model(temperature=0.1)

    def summarize(self, article: Article) -> str:
        if article.source == 'arxiv':
            return self._summarize_paper(article)
        else:
            return self._summarize_news(article)

    def _summarize_paper(self, article: Article) -> str:
        prompt_text = """
        Summarize the following AI research paper for a Korean AI Engineer.
        Use the following format strictly:
        
        **배경 (Problem):** [Problems they are trying to solve]
        **방법론 (Method):** [Key technical approach]
        **결과 (Result):** [Main performance improvements or quantitative results]
        
        Input Text:
        Title: {title}
        Abstract: {content}
        """
        prompt = ChatPromptTemplate.from_template(prompt_text)
        chain = prompt | self.llm | StrOutputParser()
        return chain.invoke({"title": article.title, "content": article.content})

    def _summarize_news(self, article: Article) -> str:
        prompt_text = """
        Summarize the following AI news in 3 bullet point sentences in Korean.
        Focus on facts and tech details.
        
        Input Text:
        Title: {title}
        Content: {content}
        """
        prompt = ChatPromptTemplate.from_template(prompt_text)
        chain = prompt | self.llm | StrOutputParser()
        return chain.invoke({"title": article.title, "content": article.content})
