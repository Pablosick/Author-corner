import sqlite3
import re
from typing import List
from datetime import datetime

from flask import url_for


class FDatabase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()
        self.cur_date = str(datetime.now().date())

    def get_menu(self, index_list: List[int]) -> List:
        try:
            get_page_title_data = f"""SELECT * FROM mainmenu WHERE id BETWEEN {index_list[0]} AND {index_list[1]}"""
            self.__cur.execute(get_page_title_data)
            res = self.__cur.fetchall()
            if res:
                return res
        except sqlite3.Error as e:
            print(f"Ошибки чтения из БД: {e}")

        return []

    def add_post(self, title: str, text: str, url: str,) -> bool:
        try:
            checking_url_address = f"SELECT COUNT() as 'count' FROM posts WHERE url LIKE '{url}'"
            self.__cur.execute(checking_url_address)
            res = self.__cur.fetchone()
            if res['count'] > 0:
                print("Статья с таким url уже существует")
                return False
            base = url_for('static', filename='img')
            text = re.sub(r"(?P<tag><img\s+[^>]*src=)(?P<quote>[\"'])(?P<url>.+?)(?P=quote)>",
                          "\\g<tag>" + base + "/\\g<url>>", text)
            self.__cur.execute("INSERT INTO posts VALUES (NULL, ?, ?, ?, ?)", (title, text, url, self.cur_date))
            self.__db.commit()
        except sqlite3.Error as e:
            print(f"Ошибка добавление статьи: {e}")
            return False

        return True

    def get_post(self, alias: str):
        try:
            get_post_from_db = f"SELECT title, text FROM posts WHERE url='{alias}' LIMIT 1"
            self.__cur.execute(get_post_from_db)
            post = self.__cur.fetchone()
            if post:
                return post
        except sqlite3.Error as e:
            print(f"Ошибки получения статьи: {e}")

        return False

    def get_all_post(self):
        try:
            receive_request_all_posts = "SELECT title, text, url FROM POSTS"
            self.__cur.execute(receive_request_all_posts)
            result = self.__cur.fetchall()
            if result:
                return result
        except sqlite3.Error as e:
            print(f"Ошибки получения всех статей: {e}")

        return []

    def user_registration(self, name: str, email: str, psw: str):
        try:
            get_required_email = f"SELECT COUNT() as 'count' FROM users WHERE email LIKE '{email}'"
            self.__cur.execute(get_required_email)
            res = self.__cur.fetchone()
            if res['count'] > 0:
                print("Пользователь с таким email уже существует")
                return False
            sing_up_req = "INSERT INTO users VALUES (NULL, ?, ?, ?, ?)"
            self.__cur.execute(sing_up_req, (name, email, psw, self.cur_date))
            self.__db.commit()
        except sqlite3.Error as e:
            print(f"Ошибка добавления данных в таблицу: {e}")
            return False

        return True

    def get_user(self, user_id):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE id = {user_id} LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print("Пользователь не найден")
                return False

            return res
        except sqlite3 as e:
            print(f"Ошибка получения данных из БД : {e}")

        return False

    def get_user_by_email(self, email):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE email='{email}' LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print("Пользователь не найден")
                return False

            return res
        except sqlite3.Error as e:
            print(f"Ошибка получения данных из БД: {e}")

        return False
