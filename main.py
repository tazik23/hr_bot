import os
from dotenv import load_dotenv

load_dotenv()

from infrastructure.vector_store.chroma_store import ChromaStore
from infrastructure.embeddings.e5_model import E5MultilingualModel
from infrastructure.llm.no_llm import NoLLM
from infrastructure.llm.ollama import OllamaLLM
from domain.chunker import DocumentChunker
from application.rag_service import RAGService
from application.document_service import DocumentService
from application.admin_service import AdminService
from presentation.console_adapter import ConsoleAdapter


def main():
    print("🚀 Запуск HR-Ассистента...")
    
    vector_store = ChromaStore()
    embedding_model = E5MultilingualModel()
    
    llm = OllamaLLM()
    
    chunker = DocumentChunker(max_chunk_size=800)
    
    document_service = DocumentService(vector_store, embedding_model, chunker)
    rag_service = RAGService(vector_store, embedding_model, llm)
    
    admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
    admin_ids = os.getenv("ADMIN_IDS", "").split(",") if os.getenv("ADMIN_IDS") else []
    admin_service = AdminService(admin_password, admin_ids)
    
    bot = ConsoleAdapter(rag_service, document_service, admin_service)
    bot.run()


if __name__ == "__main__":
    main()