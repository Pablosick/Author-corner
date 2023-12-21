import sqlite3
from typing import List
from datetime import datetime


class FDatabase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()

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

    def add_post(self, title: str, text: str) -> bool:
        try:
            cur_date = str(datetime.now().date())
            add_post_to_table = f'INSERT INTO posts VALUES (NULL, "{title}", "{text}", "{cur_date}")'
            self.__cur.execute(add_post_to_table)
            self.__db.commit()
        except sqlite3.Error as e:
            print(f"Ошибка добавление статьи: {e}")
            return False

        return True

    def get_post(self, name_post: str):
        try:
            get_post_from_db = f"SELECT text FROM posts WHERE title='{name_post}' LIMIT 1"
            self.__cur.execute(get_post_from_db)
            post = self.__cur.fetchone()
            if post is not None:
                return post[0]
        except sqlite3.Error as e:
            print(f"Ошибки получения статьи: {e}")

        return False

    def get_all_post(self):
        try:
            receive_request_all_posts = "SELECT * FROM POSTS"
            self.__cur.execute(receive_request_all_posts)
            result = self.__cur.fetchall()
            if result:
                return result
        except sqlite3.Error as e:
            print(f"Ошибки получения всех статей: {e}")

        return []

