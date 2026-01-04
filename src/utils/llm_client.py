from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
import yaml

load_dotenv()

class LLMClient:
    def __init__(self, config_path: str = "config/settings.yaml"):
        self.config = self._load_config(config_path)
        self.model_name = self.config.get("processing", {}).get("summary_model", "gpt-4o-mini")
        self.api_key = os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables.")

    def _load_config(self, path: str) -> dict:
        try:
            with open(path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            return {}

    def get_chat_model(self, temperature: float = 0.0):
        return ChatOpenAI(
            model=self.model_name,
            temperature=temperature,
            openai_api_key=self.api_key
        )
