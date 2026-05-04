import vk_api
import requests
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from presentation.base import AdminBot


class VkAdminBot(AdminBot):
    def __init__(self, document_service, admin_service, stats_service, group_token: str, group_id: int):
        super().__init__(document_service, admin_service)
        self.stats_service = stats_service
        self.group_token = group_token
        self.group_id = group_id
        self.vk = None
        self.longpoll = None
        self.waiting_for_upload = set()
        self.waiting_for_delete = set()
    
    def send_message(self, user_id: str, text: str, keyboard=None) -> None:
        params = {
            'user_id': int(user_id),
            'message': text[:4000],
            'random_id': 0
        }
        if keyboard:
            params['keyboard'] = keyboard.get_keyboard() if hasattr(keyboard, 'get_keyboard') else keyboard
        self.vk.messages.send(**params)
    
    def _get_main_keyboard(self):
        keyboard = VkKeyboard(one_time=False, inline=False)
        keyboard.add_button('📤 Загрузить документ', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('🗑️ Удалить документ', color=VkKeyboardColor.NEGATIVE)
        keyboard.add_line()
        keyboard.add_button('📋 Список документов', color=VkKeyboardColor.SECONDARY)
        keyboard.add_button('📊 Статистика', color=VkKeyboardColor.SECONDARY)
        keyboard.add_line()
        keyboard.add_button('❓ Помощь', color=VkKeyboardColor.PRIMARY)
        return keyboard
    
    def _get_help(self) -> str:
        return """
👔 HR Админ-панель

📌 Доступные действия:
  • 📤 Загрузить документ — отправьте файл (.txt, .pdf, .docx)
  • 📋 Список документов — показать все документы
  • 🗑️ Удалить документ — введите название документа
  • 📊 Статистика — показать статистику использования
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
            result += f"   {i+1}. {q['question'][:40]} ({q['count']})\n"
        
        return result
    
    def _handle_file_upload(self, user_id: str, doc) -> str:
        title = doc.get('title', 'unknown')
        ext = title.split('.')[-1].lower()
        
        if ext not in ['txt', 'pdf', 'docx']:
            return f"❌ Неподдерживаемый формат: {ext}"
        
        url = doc.get('url')
        if not url:
            return "❌ Не удалось получить файл"
        
        try:
            response = requests.get(url, timeout=30)
            if response.status_code != 200:
                return "❌ Не удалось скачать файл"
            return self.document_service.add_document_from_file(response.content, title, user_id)
        except Exception as e:
            return f"❌ Ошибка: {e}"
    
    def handle_button(self, user_id: str, button_text: str) -> str:
        if button_text == "📤 Загрузить документ":
            self.waiting_for_upload.add(user_id)
            return "📤 Отправьте файл (.txt, .pdf, .docx)"
        
        if button_text == "📋 Список документов":
            return self._format_documents_list()
        
        if button_text == "🗑️ Удалить документ":
            self.waiting_for_delete.add(user_id)
            return "🗑️ Введите название документа для удаления:"
        
        if button_text == "📊 Статистика":
            return self._format_stats()
        
        if button_text == "❓ Помощь":
            return self._get_help()
        
        return "❌ Неизвестная кнопка"
    
    def run(self):
        print("🚀 Запуск VK админ-панели...")
        
        vk_session = vk_api.VkApi(token=self.group_token)
        self.vk = vk_session.get_api()
        self.longpoll = VkBotLongPoll(vk_session, self.group_id)
        
        print("✅ Админ-панель запущена. Ожидание команд...")
        
        for event in self.longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                if event.object.message:
                    msg = event.object.message
                    user_id = str(msg['from_id'])
                    text = msg.get('text', '')
                    
                    if msg.get('attachments'):
                        for attach in msg['attachments']:
                            if attach['type'] == 'doc':
                                result = self._handle_file_upload(user_id, attach['doc'])
                                self.send_message(user_id, result, keyboard=self._get_main_keyboard())
                                self.waiting_for_upload.discard(user_id)
                                self.waiting_for_delete.discard(user_id)
                    
                    elif text:
                        if user_id in self.waiting_for_delete:
                            self.waiting_for_delete.discard(user_id)
                            deleted = self.document_service.delete_document(text.strip())
                            result = f"🗑️ Удалено {deleted} фрагментов из '{text}'"
                            self.send_message(user_id, result, keyboard=self._get_main_keyboard())
                        
                        elif user_id in self.waiting_for_upload:
                            self.waiting_for_upload.discard(user_id)
                            self.send_message(user_id, "❌ Отменено. Нажмите «📤 Загрузить документ»", keyboard=self._get_main_keyboard())
                        
                        elif text in ["📤 Загрузить документ", "📋 Список документов", "🗑️ Удалить документ", "❓ Помощь", "📊 Статистика"]:
                            result = self.handle_button(user_id, text)
                            self.send_message(user_id, result, keyboard=self._get_main_keyboard())
                        
                        else:
                            self.send_message(user_id, "❌ Используйте кнопки для управления.", keyboard=self._get_main_keyboard())