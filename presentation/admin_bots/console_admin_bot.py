from presentation.base import AdminBot


class ConsoleAdminBot(AdminBot):
    def __init__(self, document_service, admin_service, stats_service):
        super().__init__(document_service, admin_service)
        self.stats_service = stats_service
        self.current_user_id = "console_admin"
    
    def send_message(self, user_id: str, text: str) -> None:
        print(f"\n🤖 {text}")
    
    def _get_help(self) -> str:
        return """
==================================================
👔 HR-Ассистент - Админ-панель (консоль)
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
    
    def _format_documents_list(self) -> str:
        docs = self.document_service.list_documents()
        if not docs:
            return "📋 Нет документов в базе"
        return "📋 Документы:\n" + "\n".join(f"{i+1}. {d}" for i, d in enumerate(docs))
    
    def _format_stats(self) -> str:
        if not self.stats_service:
            return "📊 Статистика временно недоступна"
        
        stats = self.stats_service.get_stats()
        
        result = f"""
📊 Статистика:
• Документов: {stats['total_documents']}
• Всего вопросов: {stats['total_queries']}
• Без ответа: {stats['queries_without_answer']}
• Успешность: {stats['success_rate']}%

📈 Платформы:
"""
        for platform, count in stats['platform_stats'].items():
            result += f"   - {platform}: {count}\n"
        
        result += f"\n🔥 Топ вопросов:\n"
        for i, q in enumerate(stats['top_questions'][:5]):
            result += f"   {i+1}. {q['question'][:50]} ({q['count']})\n"
        
        return result
    
    def _handle_upload(self, filepath: str) -> str:
        try:
            with open(filepath, 'rb') as f:
                content = f.read()
            filename = filepath.split('/')[-1]
            return self.document_service.add_document_from_file(content, filename, self.current_user_id)
        except FileNotFoundError:
            return f"❌ Файл не найден: {filepath}"
        except Exception as e:
            return f"❌ Ошибка: {e}"
    
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
            return self._format_documents_list()
        
        if command == "/stats":
            return self._format_stats()
        
        if command.startswith("/delete "):
            filename = command[8:].strip()
            deleted = self.document_service.delete_document(filename)
            return f"🗑️ Удалено {deleted} фрагментов из '{filename}'"
        
        if command == "/exit":
            self.admin_service.logout(self.current_user_id)
            return "👋 Выход из админ-режима"
        
        return "❌ Неизвестная команда. /help для справки"
    
    def run(self):
        print(self._get_help())
        
        while True:
            try:
                user_input = input("\n👉 ").strip()
                
                if user_input.lower() == 'quit':
                    print("👋 До свидания!")
                    break
                
                if not user_input:
                    continue
                
                if user_input.startswith('/upload '):
                    filepath = user_input[8:].strip()
                    result = self._handle_upload(filepath)
                    print(result)
                elif user_input.startswith('/'):
                    result = self._handle_command(user_input)
                    print(result)
                else:
                    print("❌ Админ-бот не отвечает на вопросы. Используйте команды из /help")
                    
            except KeyboardInterrupt:
                print("\n👋 До свидания!")
                break
            except Exception as e:
                print(f"❌ Ошибка: {e}")