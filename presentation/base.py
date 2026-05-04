from abc import ABC, abstractmethod

class BotAdapter(ABC):
    @abstractmethod
    def run(self) -> None:
        pass
    
    @abstractmethod
    def send_message(self, user_id: str, text: str) -> None:
        pass


class PublicBot(BotAdapter, ABC):
    def __init__(self, rag_service):
        self.rag_service = rag_service
    
    def handle_question(self, question: str, platform: str = "unknown") -> str:
        return self.rag_service.ask(question, platform)

class AdminBot(BotAdapter, ABC):
    def __init__(self, document_service, admin_service):
        self.document_service = document_service
        self.admin_service = admin_service