import psycopg2

# conn = psycopg2.connect(dbname="postgres", user="postgres", password="1234", port="5432")
#
# conn.autocommit = True
#
# cursor = conn.cursor()
#
# cursor.execute("""CREATE DATABASE shedule_telegram_bot ENCODING 'UTF-8' LC_COLLATE 'en_EN.UTF-8' LC_CTYPE 'en_EN.UTF-8' TEMPLATE=template0""")
#
# cursor.close()
# conn.close()



conn = psycopg2.connect(dbname="shedule_telegram_bot", user="postgres", password="1234", port="5432")

conn.autocommit = True

cursor = conn.cursor()

cursor.execute("""ALTER TABLE IF EXISTS public.admin
    ADD FOREIGN KEY (group_id)
    REFERENCES public."group" (group_id);"""
               )

# cursor.execute(
#     "CREATE TABLE student ("
#     "student_id BIGSERIAL PRIMARY KEY,"
#     "chat_id VARCHAR(50) NOT NULL,"
#     "role VARCHAR(10),"
#     "chat_state JSON,"
#     "group_id BIGINT "
#     ")"
# )
#
# cursor.execute(
#     "CREATE TABLE hometask (id SERIAL PRIMARY KEY, group_name VARCHAR(30) NOT NULL, subject VARCHAR(100) NOT NULL, "
#     "deadline DATE NOT NULL, task TEXT NOT NULL, images JSON)")
#
# cursor.close()
# conn.close()
#
# conn = psycopg2.connect(dbname="shedule_telegram_bot", user="postgres", password="1234", port="5432")
#
# cursor = conn.cursor()
#
# cursor.execute("""INSERT INTO student (chat_id, group_name) VALUES('622603789', 'ИКБО-10-23')""")
# conn.commit()
#
# cursor.execute("""INSERT INTO admin (student_id, rule_type) VALUES(1, 'main')""")
# conn.commit()
#




cursor.close()
conn.close()