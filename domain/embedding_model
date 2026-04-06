from abc import ABC, abstractmethod
from typing import List

class EmbeddingModel(ABC):
    @abstractmethod
    def encode(self, text: str) -> List[float]:
        pass
    
    @abstractmethod
    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        pass