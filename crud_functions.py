import sqlite3
import config


connection = sqlite3.connect('database.db')
cursor = connection.cursor()


def initiate_db():
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Products(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL UNIQUE,
    description TEXT UNIQUE,
    price INTEGER NOT NULL UNIQUE,
    img_path TEXT UNIQUE)
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    email TEXT NOT NULL,
    age INTEGER NOT NULL,
    balance INTEGER NOT NULL)
    ''')
    # connection.commit()


def fill_products_table():
    for key, value in config.price.items():
        cursor.execute(f"""
        INSERT OR IGNORE INTO Products(title, description, price, img_path) 
        VALUES('{key}', '{value[1]}', '{value[2]}', '{value[0]}')
        """)
    # connection.commit()


def get_all_products():
    cursor.execute('SELECT * FROM Products')
    connection.commit()
    return cursor.fetchall()


def add_user(username, email, age, balance):
    cursor.execute(f"""
    INSERT INTO Users(username, email, age, balance)
    VALUES('{username}', '{email}', '{age}', '{balance}')
    """)
    connection.commit()


def is_included(username):
    if cursor.execute('SELECT username FROM Users WHERE username = ?', (username,)).fetchone():
        connection.commit()
        return True
    else:
        connection.commit()
        return False


if __name__ == '__main__':
    cursor.execute('DROP TABLE IF EXISTS Products')
    cursor.execute('DROP TABLE IF EXISTS Users')
    # initiate_db()
    # fill_products_table()
    # test = get_all_products()
    # for i in test:
    #     print(i)
    connection.commit()
    connection.close()