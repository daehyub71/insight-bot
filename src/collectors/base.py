from abc import ABC, abstractmethod
from typing import List
from src.state import Article

class BaseCollector(ABC):
    @abstractmethod
    def fetch_data(self) -> List[Article]:
        """Fetches data from the source and returns a list of Article objects."""
        pass
