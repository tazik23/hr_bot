import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from presentation.base import PublicBot


class VkPublicBot(PublicBot):
    def __init__(self, rag_service, group_token: str, group_id: int = None):
        super().__init__(rag_service)
        self.group_token = group_token
        self.group_id = group_id
        self.vk = None
        self.longpoll = None
    
    def send_message(self, user_id: str, text: str) -> None:
        self.vk.method('messages.send', {
            'user_id': int(user_id),
            'message': text[:4000],
            'random_id': 0
        })
    
    def run(self):
        print("🚀 Запуск публичного VK бота...")

        self.vk = vk_api.VkApi(token=self.group_token)
        self.longpoll = VkLongPoll(self.vk)
        
        print("✅ Бот запущен. Ожидание сообщений...")
        
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                user_id = str(event.user_id)
                question = event.text.strip()
                
                if question:
                    print(f"📩 Вопрос от {user_id}: {question[:100]}...")
                    answer = self.handle_question(question)
                    self.send_message(user_id, answer)
                    print(f"📤 Ответ отправлен")