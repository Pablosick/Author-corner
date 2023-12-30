class UserLogin:

    def from_db(self, user_id, db):
        self.__user = db.get_user(user_id)
        return self

    def create(self, user):
        self.__user = user
        return self

    @staticmethod
    def is_authenticated() -> bool:
        return True

    @staticmethod
    def is_active() -> bool:
        return True

    @staticmethod
    def is_anonymous() -> bool:
        return False

    def get_id(self) -> str:
        return str(self.__user['id'])

