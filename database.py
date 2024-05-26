import sqlite3


class Database:
    def __init__(self, db_file='database.db'):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()

    def create_users_table(self):
        with self.connection:
            self.cursor.execute(
                f"CREATE TABLE IF NOT EXISTS users ("
                f"telegram_id INTEGER PRIMARY KEY"
                f")"
            )
            return self.connection.commit()

    def close(self):
        self.connection.close()


class UsersDatabase(Database):
    def __init__(self):
        super().__init__()

    def add_user(self, telegram_id):
        # try:
        with self.connection:
            self.cursor.execute(
                f"INSERT OR REPLACE "
                f"INTO users(telegram_id)"
                f"VALUES ('{telegram_id}')"
            )
        self.connection.commit()
        #     return True
        # except sqlite3.IntegrityError:
        #     return False

    def delete_user(self, telegram_id):
        with self.connection:
            self.cursor.execute(
                f"DELETE "
                f"FROM users "
                f"WHERE telegram_id = {telegram_id}"
            )
        return self.connection.commit()

    def show_all_users(self):
        with self.connection:
            return self.cursor.execute(f"SELECT telegram_id FROM users").fetchall()
