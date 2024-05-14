import psycopg2

conn = psycopg2.connect(dbname="shedule_telegram_bot", user="postgres", password="1234", port="5432")
cursor = conn.cursor()

# команда для создания базы данных metanit
# sql = ("CREATE TABLE admin (id SERIAL PRIMARY KEY, chat_id VARCHAR(30) NOT NULL, student_id INT NOT NULL, rule_type "
#        "VARCHAR(20) NOT NULL)")


sql = ("CREATE TABLE student (id SERIAL PRIMARY KEY, chat_id VARCHAR(30) NOT NULL, group_name VARCHAR(30) NOT NULL, "
       "chat_state JSON)")

cursor.execute(sql)
conn.commit()
cursor.close()
conn.close()