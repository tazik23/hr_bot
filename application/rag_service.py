from domain.prompt_builder import PromptBuilder

class RAGService:
    def __init__(self, vector_store, embedding_model, llm):
        self.vector_store = vector_store
        self.embedding_model = embedding_model
        self.llm = llm
        self.prompt_builder = PromptBuilder()
    
    def ask(self, question: str) -> str:
        query_vector = self.embedding_model.encode(question)
        chunks = self.vector_store.search(query_vector, top_k=5)
        
        if not chunks:
            return "В предоставленном контексте нет достаточной информации для точного ответа."
        
        prompt = self.prompt_builder.build(chunks, question)
        return self.llm.generate(prompt)