import psycopg2

HELP = """
help - напечатать справку.
crt - Функция, создающая структуру БД (таблицы).
iph - Функция, позволяющая добавить нового клиента.
aph - Функция, позволяющая добавить телефон для существующего клиента.
chc - Функция, позволяющая изменить данные о клиенте.
dph - Функция, позволяющая удалить телефон для существующего клиента.
dcl - Функция, позволяющая удалить существующего клиента.
fcl - Функция, позволяющая найти клиента по его данным (имени, фамилии, email-у или телефону).
exit - выход из программы."""

password = input('Pass DB: ')

# conn = psycopg2.connect(database="client_db", user="postgres", password=password)
# with conn.cursor() as cur:
with psycopg2.connect(database="client_db", user="postgres", password=password) as conn:
    with conn.cursor() as cur:
        # cur.execute("""
        # DROP TABLE phones;
        # DROP TABLE users;
        # """)

        # Функция, создающая структуру БД (таблицы)
        def get_create_table():
            cur.execute("""
            CREATE TABLE IF NOT EXISTS users(
                user_id SERIAL PRIMARY KEY,
                first_name VARCHAR(40) NOT NULL,
                second_name VARCHAR(80) NOT NULL,
                email VARCHAR(25) UNIQUE
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS phones(
                phone_id SERIAL PRIMARY KEY,
                number TEXT,
                user_id INTEGER NOT NULL REFERENCES users(user_id)
                );
            """)
            conn.commit()


        def get_insert_user(first_name, second_name, email, phone=None):
            first_name = input('Укажите имя: ')
            second_name = input('Укажите фамилию: ')
            email = input('Укажите email: ')
            cur.execute("""
                INSERT INTO users(first_name, second_name, email) 
                VALUES(%s, %s, %s) 
                RETURNING user_id;
            """, (f'{first_name}', f'{second_name}', f'{email}'))
            res = cur.fetchone()[0]
            return int(res)


        # Функция, позволяющая добавить нового клиента
        def get_insert_phone(phone):
            res = get_insert_user("first_name", "second_name", "email")
            phone = input('Укажите телефон: ')
            cur.execute("""
                INSERT INTO phones(number, user_id)
                VALUES(%s, %s );
            """, (phone, res))
            conn.commit()


        # Функция, позволяющая добавить телефон для существующего клиента
        def add_phone(user_id, phone):
            phone = input('Укажите телефон: ')
            user_id = input('Введите id клиента: ')
            cur.execute("""
                INSERT INTO phones(number, user_id)
                VALUES(%s, %s );
            """, (phone, user_id))
            conn.commit()

        # Функция проверки клиента по id в БД
        def find_user_id(user_id):
            cur.execute("""
                SELECT user_id FROM users 
                WHERE user_id=%s
            """, (user_id,))
            rez = cur.fetchone()
            return rez


        # Функция, позволяющая изменить данные о клиенте
        def change_client(user_id, first_name=None, last_name=None, email=None, phones=None):
            print('Для изменения данных нужно указать id клиента и комманду!')
            print("""
                fn - Меняет Имя
                ln - Меняет Фамилию
                em - Меняет email
                ph - Меняет телефон
                ex - завершить
            """)
            user_id = input('Введите id клиента: ')
            while not find_user_id(user_id):
                user_id = input('Введите id клиента: ')
                continue
            else:
                while True:
                    command = input("Введите комманду для изменения данных: ")
                    if command == "fn":
                        fn = input('Введите новое имя: ')
                        cur.execute("""
                            UPDATE users SET first_name=%s WHERE user_id=%s;
                        """, (fn, user_id))
                        conn.commit()
                    elif command == "ln":
                        ln = input('Введите новую Фамилию: ')
                        cur.execute("""
                            UPDATE users SET last_name=%s WHERE user_id=%s;
                        """, (ln, user_id))
                        conn.commit()
                    elif command == "em":
                        em = input('Введите новый email клиента: ')
                        cur.execute("""
                            UPDATE users SET email=%s WHERE user_id=%s;
                        """, (em, user_id))
                        conn.commit()
                    elif command == "ph":
                        cur.execute("""
                            SELECT phone_id, number FROM phones WHERE user_id=%s;
                        """, (user_id,))
                        print(cur.fetchall())
                        print('Если телефонов несколько нужно указать какой меняем! ')
                        ph_id = input('Укажите порядковый номер: ')
                        ph = input('Введите новый ')
                        cur.execute("""
                            UPDATE phones SET number=%s WHERE phone_id=%s;
                        """, (ph, ph_id))
                        conn.commit()
                    elif command == "ex":
                        print("Изменения в БД сохранены!")
                        break
                    else:
                        print("Неизвестная команда, попробуйте еще раз!")


        # Функция, позволяющая удалить телефон для существующего клиента
        def delete_phone(user_id, phone):
            user_id = input('Введите id клиента: ')
            cur.execute("""
                SELECT phone_id, number FROM phones WHERE user_id=%s;
                               """, (user_id,))
            print(cur.fetchall())
            print('Если телефонов несколько нужно указать какой удаляем! ')
            phone = input('Укажите номер удаляемого телефона: ')
            cur.execute("""
                DELETE FROM phones WHERE number=%s;
            """, (phone,))
            conn.commit()


        # Функция, позволяющая удалить существующего клиента
        def delete_client(user_id):
            user_id = input('Введите id клиента: ')
            cur.execute("""
                DELETE FROM phones WHERE user_id=%s;
            """, (user_id,))
            cur.execute("""
                DELETE FROM users WHERE user_id=%s;
            """, (user_id,))
            conn.commit()


        # Функция, позволяющая найти клиента по его данным (имени, фамилии, email-у или телефону)
        def find_client(first_name=None, second_name=None, email=None, number=None):
            print('Укажите 1 любой параметр для поиска!')
            find = input(': ')
            cur.execute("""
                SELECT user_id, first_name, second_name, email, number
                FROM users
                JOIN phones USING(user_id)
                WHERE first_name=%s or second_name=%s or email=%s or number=%s
                GROUP BY user_id, number;
            """, (find, find, find, find))
            print(cur.fetchone())



        # get_create_table()
        # get_insert_phone("phone")
        # add_phone("user_id", "phone")
        # change_client("user_id")
        # delete_phone("user_id", "phone")
        # delete_client("user_id")
        # find_client()
        # cur.execute("""
        # select * from users, phones;
        # """)
        # print(cur.fetchall())

        while True:
            print("help для вызова справки по командам!")
            command = input("Введите команду: ")
            if command == "help":
                print(HELP)
            elif command == "crt":
                get_create_table()
            elif command == "iph":
                get_insert_phone("phone")
            elif command == "aph":
                add_phone("user_id", "phone")
            elif command == "chc":
                change_client("user_id")
            elif command == "dph":
                delete_phone("user_id", "phone")
            elif command == "dcl":
                delete_client("user_id")
            elif command == "fcl":
                find_client()
            elif command == "exit":
                print('Выход из программы. Спасибо за использование!')
                break
            else:
                print('Неизвестная команда! Попробуйте еще раз или посмотрите в help!')

