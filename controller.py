
# Database interactions
import json
import psycopg2
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton,Message

def read_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    return config


conn_postgres = None
def getConnection():
    global conn_postgres

    if (not conn_postgres) or conn_postgres.closed:
        config = read_config()
        conn_postgres = psycopg2.connect(dbname=config["DATABASE"]["DB"], user=config["DATABASE"]["USERNAME"],
                                         password=config["DATABASE"]["PASSWORD"], host=config["DATABASE"]["HOST"])
        conn_postgres.autocommit  = False
    return conn_postgres



async def check_user(token):
    try:
        conn = getConnection()
        print(token, type(token))
        with conn.cursor() as curs:
            curs.execute("SELECT 1 FROM public.users u WHERE u.token = %s", (token,))
            res = curs.fetchone()
            print(res)
            if not res is None:
                return True
            return False
    except Exception as e:
        print(e)
        raise e


async def update_user_info(tgid, tgusername, token):
    try:
        conn = getConnection()
        with conn.cursor() as curs:
            curs.execute("UPDATE public.users SET tg_id=%s, tg_username=%s WHERE token = %s",(tgid, tgusername, token))
            return True
    except Exception as e:
        print(e)
        raise e

async def get_userid_login_by_tgid(tgid:str):
    try:
        conn = getConnection()
        with conn.cursor() as curs:
            curs.execute("select id_user, login from public.users where tg_id=%s", (str(tgid),))
            res = curs.fetchone()
            if res is None:
                return None, None
            else:
                return res[0], res[1]
    except Exception as e:
        print(e)
        raise e

from random import choice
from string import ascii_uppercase

#print(''.join(choice(ascii_uppercase) for i in range(12)))
async def create_infobase_for_user(userid, login):
    #user_id, server_id, db_name, infobase_name, target_state, target_state_ts
    try:
        conn = getConnection()
        dbname = 'edu_'+login+'_'+''.join(choice(ascii_uppercase) for i in range(10))
        infoname = 'edu_' + login + '_' + ''.join(choice(ascii_uppercase) for i in range(10))

        with conn.cursor() as curs:
            curs.execute("INSERT INTO infobases(user_id, server_id, db_name, infobase_name, target_state_id, target_state_ts) VALUES(%s, 1, %s, %s, 1, CURRENT_TIMESTAMP)",
                         (userid, dbname, infoname))
            conn.commit()

        return dbname, infoname
    except Exception as e:
        print(e)
        raise e

async def show_active_db(userid):
    #user_id, server_id, db_name, infobase_name, target_state, target_state_ts
    try:
        conn = getConnection()

        result=[]

        with conn.cursor() as curs:
            curs.execute("SELECT infobase_id, db_name, target_state_id from infobases where ((user_id = %s) and ((target_state_id=1) or (target_state_id=2))) order by db_name",
                         (userid, ))
            result = [c[:] for c in curs.fetchall()]

        #return result
        #Строка с нумерацией и состоянием
        formatted_result = []
        for r in result:
            infobase_id = r[0]
            db_name = r[1]
            target_state_id = r[2]
            formatted_result.append(f"{infobase_id}. {db_name} - состояние: {target_state_id}")
        return formatted_result
    except Exception as e:
        print(e)
        raise e

async def register_user(tg_user_id, login):
    conn = getConnection()
    print(conn)
    try:
        with conn.cursor() as curs:
            curs.execute(f"INSERT INTO users(tg_id, tg_username) values ('{tg_user_id}', '{login}')")
        conn.commit()
        return True
    except Exception as e:
        print(e)
        if conn:
            conn.rollback()
        raise e


# Функция проверки привязки телеграмма к пользователю
async def check_user_binding(token):
    result = None
    with conn_postgres.cursor() as curs:
        curs.execute(f"SELECT 1 FROM public.users WHERE token = '{token}'")
        result = curs.fetchone()
    return result is not None


# Функция для обновления данных
async def update_user_data(tg_id, tg_username, token):
    with conn_postgres.cursor() as curs:
        curs.execute(
            f"UPDATE public.users SET tg_id = {tg_id}, tg_username = '{tg_username}' WHERE token = '{token}'")

async def choose_infobase(message: Message):
    with conn_postgres.cursor() as cursor:
        cursor.execute("SELECT infobase_name FROM public.infobases")
        infobases = cursor.fetchall()
        if infobases:
            keyboard = InlineKeyboardMarkup(row_width=1)
            for infobase in infobases:
                keyboard.add(InlineKeyboardButton(text=infobase[0], callback_data=f"infobase_{infobase[0]}"))
            await message.answer("Доступные базы:", reply_markup=keyboard)
        else:
            await message.answer("Базы данных не найдены.")



async def turnoffinfobase(infobase_id):
    try:
        conn = getConnection()
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE public.infobases SET target_state_id = 2, target_state_ts = CURRENT_TIMESTAMP WHERE db_name = %s",
                (infobase_id,)
            )
            conn.commit()
            conn.close()
    except Exception as e:
        print(f"Ошибка при отключении базы: {e}")
        raise e

async def deleteinfobase(infobase_id):
        try:
            conn = getConnection()
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE public.infobases SET target_state_id = 3 WHERE db_name = %s",
                    (infobase_id,)
                )
                conn.commit()
                conn.close()
        except Exception as e:
            print(f"Ошибка при удалении базы: {e}")
            raise e
