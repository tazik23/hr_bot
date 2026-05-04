from typing import List, Dict, Any


class PromptBuilder:
    def __init__(self):
        self.template = """You are an expert HR-assistant and must answer **only** based on the text in <context>.

Instructions:
1) Answer in the same language as the <question>; if it cannot be detected, use Russian.
2) Style — clear, neutral, with no guesses or personal opinions.
5) Do not add any information beyond <context>.
4)If you use the document At the end of your answer, specify which document(s) you used in the format: "📚 Источники: [название документа]"
5)If you not use the document - dont specify it 

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