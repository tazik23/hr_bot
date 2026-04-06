from typing import List, Dict, Any
from domain.vector_store import VectorStore
from domain.embedding_model import EmbeddingModel
from domain.llm import BaseLLM
from domain.chunker import DocumentChunker
from domain.rag_engine import RAGEngine

class RAGService:
    def __init__(
        self,
        vector_store: VectorStore,
        embedding_model: EmbeddingModel,
        llm: BaseLLM,
        chunker: DocumentChunker,
        top_k: int = 3
    ):
        self.vector_store = vector_store
        self.embedding_model = embedding_model
        self.llm = llm
        self.chunker = chunker
        self.rag_engine = RAGEngine(top_k=top_k)
    
    def ask(self, question: str) -> str:
        query_vector = self.embedding_model.encode(question)
        chunks = self.vector_store.search(query_vector, top_k=3)
        
        if not chunks:
            return "Не нашёл информации в документах."
        
        prompt = self.rag_engine.build_prompt(question, chunks)
        llm_response = self.llm.generate(prompt)
        
        return self.rag_engine.format_answer(question, chunks, llm_response)
    
    def add_document(self, text: str, metadata: Dict[str, Any]) -> int:
        chunks = self.chunker.split(text, metadata)
        
        if not chunks:
            return 0
        
        texts = [chunk["text"] for chunk in chunks]
        metadatas = [chunk["metadata"] for chunk in chunks]
        embeddings = self.embedding_model.encode_batch(texts)
        
        self.vector_store.add_documents(texts, embeddings, metadatas)
        return len(chunks)
    
    def delete_document(self, source: str) -> int:
        return self.vector_store.delete_by_source(source)
    
    def list_documents(self) -> List[str]:
        return self.vector_store.get_unique_sources()
    
    def get_stats(self) -> dict:
        return {
            "total_chunks": self.vector_store.count(),
            "total_documents": len(self.vector_store.get_unique_sources())
        }