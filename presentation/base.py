from abc import ABC, abstractmethod


class BotAdapter(ABC):
    @abstractmethod
    def run(self):
        pass
    
    @abstractmethod
    def send_message(self, user_id: str, text: str):
        pass


class PublicBot(BotAdapter, ABC):
    def __init__(self, rag_service):
        self.rag_service = rag_service
    
    @abstractmethod
    def handle_question(self, question: str):
        pass

class AdminBot(BotAdapter, ABC):
    def __init__(self, document_service, admin_service):
        self.document_service = document_service
        self.admin_service = admin_service
    
    @abstractmethod
    def handle_command(self, user_id: str, command: str):
        pass