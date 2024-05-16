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

    def start(self):
        self.add_student('ИКБО-10-23', '622603789')
        self.add_admin('ИКБО-10-23', '622603789')
        self.make_main_admin('622603789')

    def add_student(self, group_name, chat_id):
        data = self.get_student_id(chat_id)
        if data is not None:
            return 0

        with self.connection.cursor() as cursor:
            data = self.get_group_id(group_name)

            if data is None:
                cursor.execute(
                    f"""
                    INSERT INTO study_group (group_name)
                    VALUES('{group_name}')
                    RETURNING group_id
                    """
                )
                self.connection.commit()
                data = cursor.fetchone()
                if data is None:
                    return -1

            group_id, = data

            cursor.execute(
                f"""
                INSERT INTO student (chat_id, group_id)
                VALUES('{chat_id}', {group_id})
                RETURNING student_id
                """
            )
            self.connection.commit()
            data = cursor.fetchone()
            if data is None:
                return -1

            student_id, = data
            return student_id

    def add_admin(self, group_name, chat_id):
        if self.is_powered(group_name, chat_id):
            return 0

        with self.connection.cursor() as cursor:
            student_id = self.get_student_id(chat_id)
            group_id = self.get_group_id(group_name)

            if student_id is None or group_id is None:
                return -1

            cursor.execute(
                f"""
                INSERT INTO admin_relate (student_id, group_id)
                VALUES({student_id[0]}, {group_id[0]})
                RETURNING student_id
                """
            )
            self.connection.commit()
            data = cursor.fetchone()
            if data is None:
                return -1
            else:
                return 1

    def make_main_admin(self, chat_id):
        with self.connection.cursor() as cursor:
            cursor.execute(
                f"""
                UPDATE student
                SET user_role = 'main_admin'
                WHERE chat_id = '{chat_id}'
                """
            )
            self.connection.commit()

    def make_regular(self, chat_id):
        with self.connection.cursor() as cursor:
            cursor.execute(
                f"""
                UPDATE student
                SET role = NULL
                WHERE chat_id = '{chat_id}'
                """
            )
            self.connection.commit()

    def subordinate_groups(self, chat_id):
        with self.connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT study_group.group_name FROM admin_relate
                LEFT JOIN student ON student.student_id = admin_relate.student_id
                LEFT JOIN study_group ON study_group.group_id = admin_relate.group_id
                WHERE student.chat_id = '{chat_id}'
                """
            )
            data = cursor.fetchall()
            return data

    def get_role(self, chat_id):
        with self.connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT user_role FROM student WHERE chat_id = '{chat_id}' 
                """
            )
            data = cursor.fetchone()
            return data

    def get_student_id(self, chat_id):
        with self.connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT student_id FROM student WHERE chat_id = '{chat_id}'
                """
            )
            data = cursor.fetchone()
            return data

    def get_group_id(self, group_name):
        with self.connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT group_id FROM study_group WHERE group_name = '{group_name}'
                """
            )
            data = cursor.fetchone()
            return data

    def is_powered(self, group_name, chat_id):
        if self.get_role(chat_id) == 'main_admin':
            return True

        groups = self.subordinate_groups(chat_id)
        if (group_name,) not in groups:
            return False
        return True