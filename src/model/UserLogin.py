from flask import url_for

from flask_login import UserMixin


class UserLogin(UserMixin):

    def from_db(self, user_id, user):
        self.__user = user.query.filter_by(id=user_id).first()
        return self

    def create(self, user):
        self.__user = user
        return self

    def get_name(self):
        return self.__user.name if self.__user else "Без имени"

    def get_email(self):
        return self.__user.email if self.__user else "Без email"

    def get_avatar(self, app):
        img = None
        if not self.__user.avatar:
            try:
                with app.open_resource(app.root_path + url_for('static', filename='profile_usr_img/default.png'), "rb") as f:
                    img = f.read()
            except FileNotFoundError as e:
                print(f"Не найден аватар по умолчанию: {str(e)}")
        else:
            img = self.__user.avatar

        return img

    def check_file_png(self, filename):
        ext: str = filename.rsplit('.', 1)[1]
        if ext.lower() == "png":
            return True

        return False

    def get_id(self) -> str:
        return str(self.__user.id)

