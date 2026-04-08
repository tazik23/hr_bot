class AdminService:
    def __init__(self, admin_password: str, admin_ids: list = None):
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