from typing import List, Dict, Any
from domain.vector_store import VectorStore
from domain.embedding_model import EmbeddingModel
from domain.chunker import DocumentChunker
from infrastructure.text_extractor import TextExtractor


class DocumentService:
    def __init__(
        self,
        vector_store: VectorStore,
        embedding_model: EmbeddingModel,
        chunker: DocumentChunker
    ):
        self.vector_store = vector_store
        self.embedding_model = embedding_model
        self.chunker = chunker
        self.text_extractor = TextExtractor()
    
    def add_document_from_text(self, text: str, metadata: Dict[str, Any]) -> int:
        chunks = self.chunker.split(text, metadata)
        if not chunks:
            return 0
        
        texts = [chunk["text"] for chunk in chunks]
        metadatas = [chunk["metadata"] for chunk in chunks]
        embeddings = self.embedding_model.encode_batch(texts)
        
        self.vector_store.add_documents(texts, embeddings, metadatas)
        return len(chunks)
    
    def add_document_from_file(self, file_content: bytes, filename: str, uploaded_by: str) -> str:
        ext = filename.split('.')[-1].lower()
        if ext not in ['txt', 'pdf', 'docx']:
            return f"❌ Неподдерживаемый формат: {ext}"
        
        text = self.text_extractor.extract(file_content, filename)
        if not text or len(text.strip()) < 10:
            return "❌ Не удалось извлечь текст"
        
        metadata = {"source": filename, "uploaded_by": uploaded_by}
        chunks_count = self.add_document_from_text(text, metadata)
        return f"✅ Загружено {chunks_count} фрагментов"
    
    def delete_document(self, source: str) -> int:
        return self.vector_store.delete_by_source(source)
    
    def list_documents(self) -> List[str]:
        return self.vector_store.get_unique_sources()