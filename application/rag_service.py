import json
import re
from typing import List, Dict, Any
from domain.prompt_builder import PromptBuilder


class RAGService:
    def __init__(self, vector_store, embedding_model, llm, prompt_builder, stats_service=None):
        self.vector_store = vector_store
        self.embedding_model = embedding_model
        self.llm = llm
        self.prompt_builder = prompt_builder
        self.stats_service = stats_service
    
    def _extract_json(self, text: str) -> str:
        match = re.search(r'\{[^{}]*"answer"[^{}]*\}', text, re.DOTALL)
        if match:
            return match.group(0)
        return text
    
    def _validate_response(self, response: str, context_sources: set) -> Dict[str, Any]:
        try:
            json_str = self._extract_json(response)
            data = json.loads(json_str)
        except:
            return self._fallback()
        
        if "answer" not in data or "sources" not in data:
            return self._fallback()
        
        valid_sources = [s for s in data["sources"] if s in context_sources]
        data["sources"] = valid_sources
        
        if not data["sources"] and data["answer"] != "В предоставленном контексте нет достаточной информации для точного ответа.":
            return self._fallback()
        
        return data
    
    def _fallback(self) -> Dict[str, Any]:
        return {
            "answer": "В предоставленном контексте нет достаточной информации для точного ответа.",
            "sources": []
        }
    
    def ask(self, question: str, platform: str = "unknown") -> str:
        query_vector = self.embedding_model.encode(question)
        chunks = self.vector_store.search(query_vector, top_k=5)
        
        if not chunks:
            if self.stats_service:
                self.stats_service.record_query(question, False, platform)
            return "В предоставленном контексте нет достаточной информации для точного ответа."
        
        context_sources = set()
        for chunk in chunks[:5]:
            source = chunk.get("metadata", {}).get("source", "unknown")
            context_sources.add(source)
        
        prompt = self.prompt_builder.build(chunks[:5], question)
        raw_response = self.llm.generate(prompt)
        
        validated = self._validate_response(raw_response, context_sources)
        
        answer = validated["answer"]
        
        if validated["sources"]:
            answer += f"\n\n📚 Источник: {', '.join(validated['sources'])}"
        
        if self.stats_service:
            has_answer = len(validated["sources"]) > 0
            self.stats_service.record_query(question, has_answer, platform)
        
        return answer