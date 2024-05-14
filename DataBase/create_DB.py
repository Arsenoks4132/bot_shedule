import psycopg2

conn = psycopg2.connect(dbname="postgres", user="postgres", password="1234", port="5432")

conn.autocommit = True

cursor = conn.cursor()

cursor.execute("""CREATE DATABASE shedule_telegram_bot ENCODING 'UTF-8' LC_COLLATE 'en_EN.UTF-8' LC_CTYPE 'en_EN.UTF-8' TEMPLATE=template0""")

cursor.close()
conn.close()

conn = psycopg2.connect(dbname="shedule_telegram_bot", user="postgres", password="1234", port="5432")

conn.autocommit = True

cursor = conn.cursor()

cursor.execute(
    "CREATE TABLE admin (id SERIAL PRIMARY KEY, student_id INT NOT NULL, rule_type "
    "VARCHAR(20) NOT NULL)")

cursor.execute(
    "CREATE TABLE student (id SERIAL PRIMARY KEY, chat_id VARCHAR(30) NOT NULL, group_name VARCHAR(30) NOT NULL, "
    "chat_state JSON)")

cursor.execute(
    "CREATE TABLE hometask (id SERIAL PRIMARY KEY, group_name VARCHAR(30) NOT NULL, subject VARCHAR(100) NOT NULL, "
    "deadline DATE NOT NULL, task TEXT NOT NULL, images JSON)")

cursor.close()
conn.close()

conn = psycopg2.connect(dbname="shedule_telegram_bot", user="postgres", password="1234", port="5432")

cursor = conn.cursor()

cursor.execute("""INSERT INTO student (chat_id, group_name) VALUES('622603789', 'ИКБО-10-23')""")
conn.commit()

cursor.execute("""INSERT INTO admin (student_id, rule_type) VALUES(1, 'main')""")
conn.commit()

cursor.close()
conn.close()