from presentation.base import PublicBot


class ConsolePublicBot(PublicBot):
    def send_message(self, user_id: str, text: str) -> None:
        print(f"\n🤖 {text}")
    
    def _print_welcome(self) -> None:
        print("\n" + "=" * 50)
        print("🤖 Публичный HR-Ассистент (консоль)")
        print("=" * 50)
        print("Просто задайте вопрос")
        print("  quit - выход")
        print("=" * 50)

    def handle_question(self, question):
        return self.rag_service.ask(question)
    
    def run(self) -> None:
        self._print_welcome()
        
        while True:
            try:
                user_input = input("\n👉 ").strip()
                
                if user_input.lower() == "quit":
                    print("👋 До свидания!")
                    break
                
                if not user_input:
                    continue
                
                response = self.handle_question(user_input)
                self.send_message("public", response)
                
            except KeyboardInterrupt:
                print("\n👋 До свидания!")
                break
            except Exception as e:
                print(f"❌ Ошибка: {e}")