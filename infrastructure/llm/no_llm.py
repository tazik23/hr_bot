from typing import List, Dict, Any
from domain.llm import BaseLLM


class NoLLM(BaseLLM):
    def generate(self, question: str, chunks: List[Dict[str, Any]]) -> str:
        if not chunks:
            return "❌ Не нашёл информации в документах."
        
        answer = "📄 **Нашёл в документах:**\n\n"
        
        for i, chunk in enumerate(chunks[:3], 1):
            text = chunk.get("text", "").strip()
            source = chunk.get("metadata", {}).get("source", "Документ")

            if len(text) > 300:
                text = text[:300] + "..."
            
            answer += f"{i}. {text}\n   📚 {source}\n\n"
        
        return answer