import os
from typing import Optional
from infrastructure.text_extractor import TextExtractor
from application.rag_service import RAGService


class FileService:
    def __init__(self, rag_service: RAGService):
        self.rag_service = rag_service
        self.text_extractor = TextExtractor()
        self.supported_extensions = {'.txt', '.pdf', '.docx'}
        self.max_file_size = 50 * 1024 * 1024
    
    def process_uploaded_file(self, file_content: bytes, filename: str, uploaded_by: str) -> str:
        ext = os.path.splitext(filename)[1].lower()
        
        if ext not in self.supported_extensions:
            return f"Неподдерживаемый формат. Поддерживаются: {', '.join(self.supported_extensions)}"
        
        if len(file_content) > self.max_file_size:
            return f"Файл слишком большой. Максимум 50 МБ"
        
        text = self.text_extractor.extract(file_content, filename)
        
        if not text or len(text.strip()) < 10:
            return "Не удалось извлечь текст из файла"
        
        metadata = {
            "source": filename,
            "uploaded_by": uploaded_by
        }
        
        chunks_count = self.rag_service.add_document(text, metadata)
        
        return f"Документ '{filename}' загружен. Разбито на {chunks_count} фрагментов."