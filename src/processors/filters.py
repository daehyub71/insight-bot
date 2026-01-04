from src.utils.llm_client import LLMClient
from src.state import Article
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

class RelevanceFilter:
    def __init__(self):
        self.llm = LLMClient().get_chat_model(temperature=0.0)
        self.threshold = 0.7

    def filter_article(self, article: Article) -> tuple[bool, float]:
        """
        Evaluates if the article is relevant for an AI Engineer.
        Returns (is_relevant, score).
        """
        prompt_text = """
        You are an expert AI Editor. Analyze the following article title and content to determine if it is relevant and valuable for an "AI Engineer" or "Machine Learning Researcher".
        
        Criteria for good articles (Score 0.8-1.0):
        - Creating new state-of-the-art results.
        - Introducing new architectures (e.g., Transformer variants, Mamba).
        - Practical engineering improvements (e.g., optimization, quantization, deployment).
        - Major industry news (e.g., OpenAI new model, Google Gemini update).
        
        Criteria for bad articles (Score 0.0-0.6):
        - Generic AI buzzwords without technical depth.
        - Clickbait / Marketing heavy.
        - Irrelevant topics (e.g., crypto, generic tech news).
        
        Article Title: {title}
        Article Content: {content}
        
        Output ONLY a single float number between 0.0 and 1.0 representing the relevance score.
        """
        
        prompt = ChatPromptTemplate.from_template(prompt_text)
        chain = prompt | self.llm | StrOutputParser()
        
        try:
            # Truncate content to avoid context limit if necessary, though gpt-4o-mini has 128k context
            content_snippet = article.content[:2000] 
            result = chain.invoke({"title": article.title, "content": content_snippet})
            score = float(result.strip())
            return score >= self.threshold, score
        except Exception as e:
            print(f"Error filtering article {article.title}: {e}")
            return False, 0.0
