import psycopg2

class dbworker:
    def __init__(self, host, user, password, db_name):
        self.connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=db_name
        )
        self.cursor = self.connection.cursor()
        self.create_tables()

    def create_tables(self):
        with self.connection:

            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    telegram_id BIGINT PRIMARY KEY,
                    telegram_username TEXT,
                    full_name TEXT
                )
            ''')
 
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS apartments (
                    id SERIAL PRIMARY KEY,
                    telegram_id BIGINT,
                    city TEXT,
                    address TEXT,
                    price INTEGER,
                    description TEXT,
                    type TEXT,  
                    area FLOAT, 
                    photos TEXT  
                )
            ''')

    def add_user(self, telegram_username, telegram_id, full_name):
        with self.connection:
            return self.cursor.execute("INSERT INTO users(telegram_username, telegram_id, full_name) VALUES (%s, %s, %s)", (telegram_username, telegram_id, full_name))

    def user_exists(self, user_id):
        with self.connection:
            self.cursor.execute('SELECT * FROM users WHERE telegram_id = %s', (user_id,))
            result = self.cursor.fetchall()
            return bool(result)

    def add_apartment(self, telegram_id, city, address, price, description, apartment_type, area, photos):
        with self.connection:
            return self.cursor.execute(
                "INSERT INTO apartments(telegram_id, city, address, price, description, type, area, photos) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (telegram_id, city, address, price, description, apartment_type, area, photos)
            )

    def get_all_apartments(self):
        with self.connection:
            self.cursor.execute("SELECT * FROM apartments")
            return self.cursor.fetchall()

    def delete_apartment(self, apartment_id):
        with self.connection:
            return self.cursor.execute("DELETE FROM apartments WHERE id = %s", (apartment_id,))