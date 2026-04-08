from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseLLM(ABC):
    @abstractmethod
    def generate(self, question: str, chunks: List[Dict[str, Any]]) -> str:
        pass