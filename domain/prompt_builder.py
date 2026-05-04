from typing import List, Dict, Any


class PromptBuilder:
    def __init__(self):
        self.template = """You are an HR assistant. You must answer ONLY using the provided context.
Return your answer strictly in JSON:
{{
  "answer": string,
  "sources": string[]
}}
Rules:
- Use ONLY information from the context
- Do NOT guess, infer, or add anything
- Sources must EXACTLY match document names from the context
- If unsure about a source — do not include it
- If the answer is not explicitly in the context:
  return:
  {{
    "answer": "В предоставленном контексте нет достаточной информации для точного ответа.",
    "sources": []
  }}
---
Example 1:
Context:
<document>
name: doc1
content: Компания работает 5 дней в неделю.
</document>
Question:
Сколько дней работает компания?
Output:
{{
  "answer": "Компания работает 5 дней в неделю.",
  "sources": ["doc1"]
}}
---
Example 2:
Context:
<document>
name: doc1
content: Компания занимается IT-консалтингом.
</document>
Question:
Какая зарплата у сотрудников?
Output:
{{
  "answer": "В предоставленном контексте нет достаточной информации для точного ответа.",
  "sources": []
}}
---
Now answer:
Context:
{context}
Question:
{question}
"""
    
    def build(self, chunks: List[Dict[str, Any]], question: str) -> str:
        context_parts = []
        
        for chunk in chunks[:5]:
            source = chunk.get("metadata", {}).get("source", "unknown")
            text = chunk.get("text", "").strip()
            
            context_parts.append(
                f"<document>\nname: {source}\ncontent: {text}\n</document>"
            )
        
        context = "\n\n".join(context_parts)
        
        return self.template.format(
            context=context,
            question=question.strip()
        )