import psycopg2


class Database:
    def __init__(self):
        self.connection = psycopg2.connect(
            dbname='shedule_telegram_bot',
            user='postgres',
            password='1234',
            port='5432'
        )

    def __del__(self):
        self.connection.close()

    def student_group(self, chat_id: str) -> tuple[str, ...] | None:
        with self.connection.cursor() as cursor:
            cursor.execute(f"""SELECT group_name FROM student WHERE chat_id='{chat_id}'""")
            data = cursor.fetchone()
            if data is None:
                return None
            else:
                return data[0]

    def student_id(self, chat_id: str) -> int:
        with self.connection.cursor() as cursor:
            cursor.execute(f"""SELECT id FROM student WHERE chat_id='{chat_id}'""")
            data = cursor.fetchone()
            if data is None:
                return -1
            else:
                return data[0]

    def admin_rule_type(self, student_id: int) -> str:
        with self.connection.cursor() as cursor:
            cursor.execute(f"""SELECT rule_type FROM admin WHERE student_id={student_id}""")
            data = cursor.fetchone()
            if data is None:
                return 'regular_user'
            else:
                return data[0]

    def add_student(self, chat_id: str, group_name: str) -> int:
        with self.connection.cursor() as cursor:
            cursor.execute(
                f"""INSERT INTO student (chat_id, group_name) VALUES('{chat_id}', '{group_name}') RETURNING id"""
            )
            self.connection.commit()
            new_id = cursor.fetchone()
            if new_id is None:
                return -1
            else:
                return new_id[0]

    def add_admin(self, student_id: int, rule_type: str):
        with self.connection.cursor() as cursor:
            cursor.execute(
                f"""INSERT INTO admin (student_id, rule_type) VALUES('{student_id}', '{rule_type}')"""
            )
            self.connection.commit()