import psycopg2
from DataBase.utilities import e


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
                    VALUES('{e(group_name)}')
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
                VALUES('{e(chat_id)}', {group_id})
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
                WHERE chat_id = '{e(chat_id)}'
                """
            )
            self.connection.commit()

    def make_regular(self, chat_id):
        with self.connection.cursor() as cursor:
            cursor.execute(
                f"""
                UPDATE student
                SET role = NULL
                WHERE chat_id = '{e(chat_id)}'
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
                WHERE student.chat_id = '{e(chat_id)}'
                """
            )
            data = cursor.fetchall()
            return data

    def get_role(self, chat_id):
        with self.connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT user_role FROM student WHERE chat_id = '{e(chat_id)}' 
                """
            )
            data = cursor.fetchone()
            return data

    def get_group_name(self, chat_id):
        with self.connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT study_group.group_name FROM student
                LEFT JOIN study_group USING (group_id)
                WHERE student.chat_id = '{e(chat_id)}'
                """
            )
            data = cursor.fetchone()
            return data

    def get_student_id(self, chat_id):
        with self.connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT student_id FROM student WHERE chat_id = '{e(chat_id)}'
                """
            )
            data = cursor.fetchone()
            return data

    def get_group_id(self, group_name):
        with self.connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT group_id FROM study_group WHERE group_name = '{e(group_name)}'
                """
            )
            data = cursor.fetchone()
            return data

    def is_powered(self, group_name, chat_id):
        if self.get_role(chat_id) == ('main_admin',):
            return True

        groups = self.subordinate_groups(chat_id)
        if (group_name,) not in groups:
            return False
        return True

    def subjects_list(self, group_name):
        with self.connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT DISTINCT hometask.subject FROM hometask
                LEFT JOIN study_group USING (group_id)
                WHERE study_group.group_name = '{e(group_name)}'
                ORDER BY hometask.subject
                """
            )
            data = cursor.fetchall()
            return data

    def date_list(self, group_name, subject):
        with self.connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT DISTINCT hometask.deadline FROM hometask
                LEFT JOIN study_group USING (group_id)
                WHERE study_group.group_name = '{e(group_name)}' AND hometask.subject = '{e(subject)}'
                ORDER BY hometask.deadline
                """
            )
            data = cursor.fetchall()
            return data

    def add_hometask(self, data):
        with self.connection.cursor() as cursor:
            group_id = self.get_group_id(data['chosen_group'])
            if group_id is None:
                return -1
            cursor.execute(
                f"""
                INSERT INTO hometask
                (subject, deadline, task, group_id)
                VALUES ('{e(data['entered_subject'])}',
                '{data['entered_date'].strftime('%Y-%m-%d')}', 
                '{e(data['entered_text'])}', {group_id[0]})
                RETURNING hometask_id
                """
            )
            self.connection.commit()

            ht_id = cursor.fetchone()
            if ht_id is None:
                return -1
            if 'sent_images' not in data:
                return ht_id[0]
            images = data['sent_images']
            for image in images:
                cursor.execute(
                    f"""
                    INSERT INTO image
                    (server_id, hometask_id)
                    VALUES ('{image}', {ht_id[0]})
                    """
                )
                self.connection.commit()
            return ht_id[0]

    def get_hometask(self, hometask_id):
        with self.connection.cursor() as cursor:
            ht_data = dict()
            cursor.execute(
                f"""
                SELECT * FROM hometask
                LEFT JOIN study_group USING (group_id)
                WHERE hometask.hometask_id = {hometask_id}
                """
            )
            data = cursor.fetchone()
            if cursor is None:
                return None
            ht_data['group'] = data[5]
            ht_data['subject'] = data[2]
            ht_data['date'] = data[3]
            ht_data['task'] = data[4]

            cursor.execute(
                f"""
                SELECT server_id FROM image
                WHERE hometask_id = {hometask_id}
                """
            )
            data = cursor.fetchall()
            if data is not None:
                ht_data['images'] = [item[0] for item in data]
            else:
                ht_data['images'] = []
            return ht_data

    def get_hometask_id(self, group_name, subject, deadline):
        with self.connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT hometask.hometask_id FROM hometask
                LEFT JOIN study_group USING (group_id)
                WHERE study_group.group_name = '{group_name}' AND
                hometask.subject = '{subject}' AND hometask.deadline = '{deadline.strftime('%Y-%m-%d')}'
                """
            )
            data = cursor.fetchone()
            return data


