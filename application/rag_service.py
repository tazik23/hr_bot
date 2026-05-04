from domain.prompt_builder import PromptBuilder

class RAGService:
    def __init__(self, vector_store, embedding_model, llm, prompt_builder, stats_service=None):
        self.vector_store = vector_store
        self.embedding_model = embedding_model
        self.llm = llm
        self.prompt_builder = prompt_builder
        self.stats_service = stats_service
    
    def ask(self, question: str, platform: str = "unknown") -> str:
        query_vector = self.embedding_model.encode(question)
        chunks = self.vector_store.search(query_vector, top_k=5)
        
        no_answer_phrases = [
            "нет достаточной информации",
            "не нашёл информации",
            "не удалось найти",
            "в предоставленном контексте нет"
        ]
        
        if not chunks:
            answer = "В предоставленном контексте нет достаточной информации для точного ответа."
            has_answer = False
        else:
            prompt = self.prompt_builder.build(chunks, question)
            answer = self.llm.generate(prompt)
            
            answer_lower = answer.lower()
            has_answer = not any(phrase in answer_lower for phrase in no_answer_phrases)
        
        if self.stats_service:
            self.stats_service.record_query(question, has_answer, platform)
        
        return answer