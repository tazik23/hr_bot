class ConsoleAdapter:
    def __init__(self, rag_service, document_service, admin_service):
        self.rag_service = rag_service
        self.document_service = document_service
        self.admin_service = admin_service
        self.current_user_id = "console_user"
    
    def _get_help(self) -> str:
        return """
==================================================
HR-Ассистент - Консольная версия
==================================================
Команды:
  /admin <пароль>  - войти в админ-режим
  /upload <путь>   - загрузить документ
  /list            - список документов
  /delete <имя>    - удалить документ
  /stats           - статистика
  /exit            - выйти из админ-режима
  /help            - показать справку
  Любой текст      - задать вопрос
  quit             - выйти из программы
==================================================
"""
    
    def _handle_command(self, command: str) -> str:
        if command == "/help":
            return self._get_help()
        
        if command.startswith("/admin"):
            parts = command.split(maxsplit=1)
            password = parts[1] if len(parts) > 1 else ""
            if self.admin_service.authenticate(self.current_user_id, password):
                return "✅ Админ-режим активирован"
            return "❌ Неверный пароль"
        
        if not self.admin_service.is_admin(self.current_user_id):
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
                return self.document_service.add_document_from_file(content, filename, self.current_user_id)
            except FileNotFoundError:
                return f"❌ Файл не найден"
        
        elif command == "/exit":
            self.admin_service.logout(self.current_user_id)
            return "👋 Выход из админ-режима"
        
        return "❌ Неизвестная команда"
    
    def run(self):
        print(self._get_help())
        
        while True:
            user_input = input("\n👉 ").strip()
            
            if user_input.lower() == 'quit':
                print("👋 До свидания!")
                break
            
            if not user_input:
                continue
            
            if user_input.startswith('/'):
                print(self._handle_command(user_input))
            else:
                print(f"\n🤖 {self.rag_service.ask(user_input)}")