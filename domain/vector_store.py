from abc import ABC, abstractmethod
from typing import List, Dict, Any

class VectorStore(ABC):
    @abstractmethod
    def add_documents(
        self, 
        texts: List[str], 
        embeddings: List[List[float]], 
        metadatas: List[Dict[str, Any]]
    ) -> None:
        pass
    
    @abstractmethod
    def search(
        self, 
        query_embedding: List[float], 
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def delete_by_source(self, source: str) -> int:
        pass
    
    @abstractmethod
    def get_unique_sources(self) -> List[str]:
        pass
    
    @abstractmethod
    def count(self) -> int:
        pass