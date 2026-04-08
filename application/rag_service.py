from domain.vector_store import VectorStore
from domain.embedding_model import EmbeddingModel
from domain.llm import BaseLLM


class RAGService:
    def __init__(
        self,
        vector_store: VectorStore,
        embedding_model: EmbeddingModel,
        llm: BaseLLM
    ):
        self.vector_store = vector_store
        self.embedding_model = embedding_model
        self.llm = llm
    
    def ask(self, question: str) -> str:
        query_vector = self.embedding_model.encode(question)
        chunks = self.vector_store.search(query_vector, top_k=3)
        return self.llm.generate(question, chunks)