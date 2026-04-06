from typing import List, Dict, Any, Optional

class RAGEngine:
    def __init__(self, top_k: int = 3):
        self.top_k = top_k
    
    def build_prompt(self, question: str, chunks: List[Dict[str, Any]]) -> str:
        if not chunks:
            return question
        
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            source = chunk.get("metadata", {}).get("source", "Неизвестный источник")
            text = chunk.get("text", "")
            context_parts.append(f"[{i}] Источник: {source}\n{text}")
        
        context = "\n\n---\n\n".join(context_parts)
  
        prompt = f"""Ты — HR-ассистент компании. Отвечай на вопросы сотрудников, используя ТОЛЬКО информацию из предоставленных документов.

Если ответа нет в документах — скажи: «Не нашёл информации в документах».

ВОПРОС: {question}

ДОКУМЕНТЫ:
{context}

ОТВЕТ:"""
        
        return prompt
    
    def format_answer(
        self, 
        question: str, 
        chunks: List[Dict[str, Any]], 
        llm_response: Optional[str] = None
    ) -> str:
        if not chunks:
            return "Не нашёл информации в документах по вашему вопросу."
        
        if llm_response:
            answer = llm_response
        else:
            answer = "Нашёл в документах:\n\n"
            for i, chunk in enumerate(chunks, 1):
                text = chunk.get("text", "")
                source = chunk.get("metadata", {}).get("source", "Документ")
                answer += f"{i}. {text}\n\n"

        sources = set()
        for chunk in chunks:
            source = chunk.get("metadata", {}).get("source", "Документ")
            sources.add(source)
        
        if sources:
            answer += "\n\n*Источники:*\n"
            for source in sources:
                answer += f"* {source}\n"
        
        return answer