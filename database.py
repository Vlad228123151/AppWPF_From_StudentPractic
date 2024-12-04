import psycopg2
from psycopg2 import sql

class Database:
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname="tax_calculator_db",
            user="postgres",  # Замените на вашего пользователя PostgreSQL
            password="1234",  # Замените на ваш пароль
            host="localhost",
            port="5432"
        )
        self.cursor = self.conn.cursor()

    def execute_query(self, query, params=None):
        """Выполняет SQL-запрос."""
        if params:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query)
        self.conn.commit()

    def fetch_all(self, query, params=None):
        """Выполняет запрос и возвращает все результаты."""
        if params:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query)
        return self.cursor.fetchall()

    def add_deduction(self, deduction_name, amount):
        """Добавление нового вычета."""
        query = "INSERT INTO deductions (deduction_name, amount) VALUES (%s, %s)"
        self.execute_query(query, (deduction_name, amount))

    def update_deduction(self, deduction_id, new_name, new_amount):
        """Редактирование существующего вычета."""
        query = "UPDATE deductions SET deduction_name=%s, amount=%s WHERE id=%s"
        self.execute_query(query, (new_name, new_amount, deduction_id))

    def delete_deduction(self, deduction_id):
        """Удаление вычета."""
        query = "DELETE FROM deductions WHERE id=%s"
        self.execute_query(query, (deduction_id,))

    def add_tax_rate(self, rate_name, rate_percentage):
        """Добавление новой ставки налога."""
        query = "INSERT INTO tax_rates (rate_name, rate_percentage) VALUES (%s, %s)"
        self.execute_query(query, (rate_name, rate_percentage))

    def update_tax_rate(self, tax_rate_id, new_name, new_percentage):
        """Редактирование существующей ставки налога."""
        query = "UPDATE tax_rates SET rate_name=%s, rate_percentage=%s WHERE id=%s"
        self.execute_query(query, (new_name, new_percentage, tax_rate_id))

    def delete_tax_rate(self, tax_rate_id):
        """Удаление ставки налога."""
        query = "DELETE FROM tax_rates WHERE id=%s"
        self.execute_query(query, (tax_rate_id,))

    def close(self):
        """Закрывает соединение с базой данных."""
        self.cursor.close()
        self.conn.close()