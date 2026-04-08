import os
import requests
from domain.llm import BaseLLM


class OllamaLLM(BaseLLM):
    def __init__(self, model: str = None, host: str = None):
        self.model = model or os.getenv("OLLAMA_MODEL")
        self.host = host or os.getenv("OLLAMA_HOST")
    
    def generate(self, prompt: str) -> str:
        try:
            response = requests.post(
                f"{self.host}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False},
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json()["response"]
            else:
                return f"❌ Ошибка Ollama: {response.status_code}"
        except requests.exceptions.ConnectionError:
            return "❌ Ollama не запущен. Запустите 'ollama serve'"
        except Exception as e:
            return f"❌ Ошибка: {e}"