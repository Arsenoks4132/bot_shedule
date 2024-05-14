import psycopg2

conn = psycopg2.connect(dbname="shedule_telegram_bot", user="postgres", password="1234", port="5432")

cursor = conn.cursor()

cursor.execute("""INSERT INTO admin (chat_id, student_id, rule_type) VALUES('622603789', 1, 'main')""")
conn.commit()

cursor.close()
conn.close()