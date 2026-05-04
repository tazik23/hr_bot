import os
import threading
from dotenv import load_dotenv

load_dotenv()

from infrastructure.vector_store.chroma_store import ChromaStore
from infrastructure.embeddings.e5_model import E5MultilingualModel
from domain.chunker import DocumentChunker
from application.rag_service import RAGService
from application.document_service import DocumentService
from application.admin_service import AdminService
from application.stats_service import StatsService
from domain.prompt_builder import PromptBuilder


def get_llm():
    llm_mode = os.getenv("LLM_MODE")
    
    if llm_mode == "ollama":
        from infrastructure.llm.ollama import OllamaLLM
        return OllamaLLM()
    else:
        from infrastructure.llm.no_llm import NoLLM
        return NoLLM()


def run_public_bot(rag_service):
    platform = os.getenv("PUBLIC_PLATFORM", "console")
    
    if platform == "vk":
        token = os.getenv("VK_GROUP_TOKEN")
        from presentation.public_bots.vk_public_bot import VkPublicBot
        bot = VkPublicBot(rag_service, token)
    else:
        from presentation.public_bots.console_public_bot import ConsolePublicBot
        bot = ConsolePublicBot(rag_service)
    
    bot.run()


def run_admin_bot(document_service, admin_service, stats_service):
    platform = os.getenv("ADMIN_PLATFORM", "console_admin")
    
    if platform == "vk":
        token = os.getenv("VK_ADMIN_TOKEN")
        group_id = int(os.getenv("VK_ADMIN_GROUP_ID"))
        from presentation.admin_bots.vk_admin_bot import VkAdminBot
        bot = VkAdminBot(document_service, admin_service, stats_service, token, group_id)
    else:
        from presentation.admin_bots.console_admin_bot import ConsoleAdminBot
        bot = ConsoleAdminBot(document_service, admin_service, stats_service)
    
    bot.run()


def main():
    print("🚀 Запуск HR-Ассистента...")
    vector_store = ChromaStore()
    embedding_model = E5MultilingualModel()
    chunker = DocumentChunker()
    prompt_builder = PromptBuilder()
    
    llm = get_llm()
    stats_service = StatsService(vector_store)
    
    rag_service = RAGService(
        vector_store=vector_store,
        embedding_model=embedding_model,
        llm=llm,
        prompt_builder=prompt_builder,
        stats_service=stats_service
    )
    
    document_service = DocumentService(vector_store, embedding_model, chunker)
    
    admin_password = os.getenv("ADMIN_PASSWORD")
    admin_ids = os.getenv("ADMIN_IDS").split(",") if os.getenv("ADMIN_IDS") else []
    admin_service = AdminService(admin_password, admin_ids)
    
    public_thread = threading.Thread(target=run_public_bot, args=(rag_service,))
    admin_thread = threading.Thread(target=run_admin_bot, args=(document_service, admin_service, stats_service))
    
    public_thread.start()
    admin_thread.start()
    
    public_thread.join()
    admin_thread.join()


if __name__ == "__main__":
    main()