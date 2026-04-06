class AdminService:
    def __init__(self, rag_service, admin_password: str, admin_ids: list = None):
        self.rag_service = rag_service
        self.admin_password = admin_password
        self.admin_ids = admin_ids or []
        self.active_sessions = set()
    
    def authenticate(self, user_id: str, password: str = None) -> bool:
        if str(user_id) in self.admin_ids:
            self.active_sessions.add(str(user_id))
            return True
        
        if password and password == self.admin_password:
            self.active_sessions.add(str(user_id))
            return True
        
        return False
    
    def is_admin(self, user_id: str) -> bool:
        return str(user_id) in self.active_sessions
    
    def logout(self, user_id: str):
        self.active_sessions.discard(str(user_id))
    
    def handle_command(self, user_id: str, command: str) -> str:
        if not self.is_admin(user_id):
            return "Нет доступа. Используйте /admin"
        
        if command == "/list":
            docs = self.rag_service.list_documents()
            if not docs:
                return "Нет документов в базе"
            result = "Документы:\n"
            for i, doc in enumerate(docs, 1):
                result += f"{i}. {doc}\n"
            return result
        
        elif command.startswith("/delete "):
            filename = command[8:].strip()
            deleted = self.rag_service.delete_document(filename)
            return f"Удалено {deleted} фрагментов из '{filename}'"
        
        elif command == "/stats":
            stats = self.rag_service.get_stats()
            return f"Статистика:\n Документов: {stats['total_documents']}\n Фрагментов: {stats['total_chunks']}"
        
        elif command == "/exit":
            self.logout(user_id)
            return "Выход из админ-режима"
        
        return "Неизвестная команда. Доступно: /list, /delete <имя>, /stats, /exit"