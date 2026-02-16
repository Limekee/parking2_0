"""файл нужный только для теста, подключена ли бд из Postgrasql или нет"""

# import psycopg2

# try:
#     conn = psycopg2.connect(
#         host="localhost",
#         database="parking",
#         user="postgres",
#         password="12345678",
#         port="5432"
#     )
#     print("Подключение успешно!")
#     conn.close()
# except Exception as e:
#     print(f"Ошибка подключения: {e}")

from uuid import uuid4

print(uuid4())