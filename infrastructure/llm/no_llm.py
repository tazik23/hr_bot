from domain.llm import BaseLLM


class NoLLM(BaseLLM):
    def generate(self, prompt: str) -> str:
        return None