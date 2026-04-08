from typing import List, Dict, Any


class PromptBuilder:
    def __init__(self):
        self.template = """You are an expert HR-assistant and must answer **only** based on the text in <context>.

Instructions:
1) Answer in the same language as the <question>; if it cannot be detected, use Russian.
2) Style — clear, neutral, with no guesses or personal opinions.
3) Keep terminology as in the <context>.
4) At the end of your answer, specify which document(s) you used in the format: "📚 Источники: [название документа]"
5) Do not add any information beyond <context>.
6) If the required information is missing, answer ONLY: "В предоставленном контексте нет достаточной информации для точного ответа. Do NOT add any source in this case."

<Context>
{context}
</Context>

<Question>
{question}
</Question>"""
    
    def build(self, chunks: List[Dict[str, Any]], question: str) -> str:
        context_parts = []
        for chunk in chunks:
            source = chunk.get("metadata", {}).get("source", "Неизвестный источник")
            text = chunk.get("text", "")
            context_parts.append(f"[Источник: {source}]\n{text}")
        
        context = "\n\n---\n\n".join(context_parts)
        
        return self.template.format(context=context, question=question)