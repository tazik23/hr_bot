from abc import ABC, abstractmethod
from typing import Optional
from application.rag_service import RAGService
from application.admin_service import AdminService
from application.document_service import FileService


class BotAdapter(ABC):
    def __init__(
        self,
        rag_service: RAGService,
        admin_service: AdminService,
        file_service: FileService
    ):
        self.rag_service = rag_service
        self.admin_service = admin_service
        self.file_service = file_service
        self.current_user_id: Optional[str] = None
    
    @abstractmethod
    def send_message(self, user_id: str, text: str) -> None:
        pass
    
    @abstractmethod
    def run(self) -> None:
        pass
    
    def _handle_text_message(self, user_id: str, text: str) -> str:
        if text.startswith('/'):
            return self.admin_service.handle_command(user_id, text)
        return self.rag_service.ask(text)