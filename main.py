import os
from dotenv import load_dotenv

load_dotenv()

from infrastructure.vector_store.chroma_store import ChromaStore
from infrastructure.embeddings.e5_model import E5MultilingualModel
from domain.chunker import DocumentChunker
from application.rag_service import RAGService
from application.document_service import DocumentService
from application.admin_service import AdminService
from domain.prompt_builder import PromptBuilder


def get_llm():
    llm_mode = os.getenv("LLM_MODE")
    
    if llm_mode == "ollama":
        from infrastructure.llm.ollama import OllamaLLM
        return OllamaLLM()
    else:
        from infrastructure.llm.no_llm import NoLLM
        return NoLLM()


def main():    
    vector_store = ChromaStore()
    embedding_model = E5MultilingualModel()
    chunker = DocumentChunker(800)
    prompt_builder = PromptBuilder()
    
    llm = get_llm()
    
    rag_service = RAGService(
        vector_store=vector_store,
        embedding_model=embedding_model,
        llm=llm,
        prompt_builder=prompt_builder,
    )
    
    document_service = DocumentService(vector_store, embedding_model, chunker)
    
    admin_password = os.getenv("ADMIN_PASSWORD")
    admin_ids = os.getenv("ADMIN_IDS").split(",") if os.getenv("ADMIN_IDS") else []
    admin_service = AdminService(admin_password, admin_ids)
    
    bot_type = os.getenv("BOT_TYPE", "public")
    bot_platform = os.getenv("BOT_PLATFORM", "console")
    
    if bot_platform == "console":
        print("🚀 Запуск HR-Ассистента...")
        if bot_type == "admin":
            from presentation.admin_bots.console_admin_bot import ConsoleAdminBot
            bot = ConsoleAdminBot(document_service, admin_service)
            print("👔 Запуск консольной админ-панели")
        else:
            from presentation.public_bots.console_public_bot import ConsolePublicBot
            bot = ConsolePublicBot(rag_service)
            print("👥 Запуск публичного консольного бота")
    else:
        raise ValueError(f"Неизвестная платформа: {bot_platform}")
    
    bot.run()

if __name__ == "__main__":
    main()