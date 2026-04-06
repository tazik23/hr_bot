import io
from typing import Optional

class TextExtractor:
    def extract(self, file_content: bytes, filename: str) -> Optional[str]:
        ext = filename.split('.')[-1].lower()
        
        if ext == 'txt':
            return file_content.decode('utf-8', errors='ignore')
        
        elif ext == 'pdf':
            return self._extract_pdf(file_content)
        
        elif ext == 'docx':
            return self._extract_docx(file_content)
        
        return None
    
    def _extract_pdf(self, file_content: bytes) -> str:
        try:
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(file_content))
            text = "\n".join([page.extract_text() or "" for page in reader.pages])
            return text
        except Exception as e:
            return f"[Ошибка PDF: {e}]"
    
    def _extract_docx(self, file_content: bytes) -> str:
        try:
            from docx import Document
            doc = Document(io.BytesIO(file_content))
            text = "\n".join([para.text for para in doc.paragraphs])
            return text
        except Exception as e:
            return f"[Ошибка DOCX: {e}]"