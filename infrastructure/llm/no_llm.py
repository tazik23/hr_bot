from domain.llm import BaseLLM
import re

class NoLLM(BaseLLM):
    def generate(self, prompt: str) -> str:
        match = re.search(r'<Context>(.*?)</Context>', prompt, re.DOTALL)
        if not match:
            return "❌ Не нашёл информации."
        
        context = match.group(1).strip()
        blocks = re.split(r'---\n\n', context)
        
        answer = "📄 **Нашёл в документах:**\n\n"
        seen = set()
        
        for block in blocks:
            source_match = re.search(r'\[Источник: (.*?)\]', block)
            source = source_match.group(1) if source_match else "Неизвестный источник"
            
            text_match = re.search(r'\]\n(.*?)$', block, re.DOTALL)
            text = text_match.group(1).strip() if text_match else ""
            
            if text in seen:
                continue
            seen.add(text)
            
            if len(text) > 500:
                text = text[:500] + "..."
            
            answer += f"• **{source}**\n  {text}\n\n"
        
        return answer.strip()