from presentation.base import AdminBot


class ConsoleAdminBot(AdminBot):
    def __init__(self, document_service, admin_service):
        self.current_user_id = "console_admin"
        super().__init__(document_service, admin_service)
    
    def _get_help(self) -> str:
        return """
==================================================
HR-Ассистент - Админ-панель (консоль)
==================================================
Команды:
  /admin <пароль>  - войти в админ-режим
  /upload <путь>   - загрузить документ
  /list            - список документов
  /delete <имя>    - удалить документ
  /stats           - статистика
  /exit            - выйти из админ-режима
  /help            - показать справку
  quit             - выйти из программы
==================================================
"""
    
    def handle_command(self, user_id: str, command: str) -> str:
        if command == "/help":
            return self._get_help()
        
        if command.startswith("/admin"):
            parts = command.split(maxsplit=1)
            password = parts[1] if len(parts) > 1 else ""
            if self.admin_service.authenticate(user_id, password):
                return "✅ Админ-режим активирован"
            return "❌ Неверный пароль"
        
        if not self.admin_service.is_admin(user_id):
            return "❌ Нет доступа. Используйте /admin"
        
        if command == "/list":
            docs = self.document_service.list_documents()
            if not docs:
                return "📋 Нет документов"
            return "📋 Документы:\n" + "\n".join(f"{i+1}. {d}" for i, d in enumerate(docs))
        
        elif command.startswith("/delete "):
            filename = command[8:].strip()
            deleted = self.document_service.delete_document(filename)
            return f"🗑️ Удалено {deleted} фрагментов"
        
        elif command.startswith("/upload "):
            filepath = command[8:].strip()
            try:
                with open(filepath, 'rb') as f:
                    content = f.read()
                filename = filepath.split('/')[-1]
                return self.document_service.add_document_from_file(content, filename, user_id)
            except FileNotFoundError:
                return "❌ Файл не найден"
            except Exception as e:
                return f"❌ Ошибка: {e}"
        
        elif command == "/stats":
            stats = self.stats_service.get_stats() if hasattr(self, 'stats_service') else {"total_documents": 0, "total_chunks": 0}
            return f"📊 Статистика:\n• Документов: {stats['total_documents']}\n• Фрагментов: {stats['total_chunks']}"
        
        elif command == "/exit":
            self.admin_service.logout(user_id)
            return "👋 Выход из админ-режима"
        
        return "❌ Неизвестная команда"
    
    def send_message(self, user_id: str, text: str) -> None:
        print(text)
    
    def run(self):
        print(self._get_help())
        
        while True:
            user_input = input("\n👉 ").strip()
            
            if user_input.lower() == 'quit':
                print("👋 До свидания!")
                break
            
            if not user_input:
                continue
            
            else:
                print(self.handle_command(self.current_user_id, user_input))