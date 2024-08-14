import asyncio
import logging
from aiogram import Bot
from aiogram import Dispatcher
from aiogram import types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters.command import Command
import sys
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, BotCommand
from aiogram.utils.callback_answer import CallbackAnswer
from aiogram.exceptions import TelegramForbiddenError
import json
import pymssql
import datetime
from controller import turnoffinfobase, deleteinfobase, show_active_db, check_user, update_user_info, get_userid_login_by_tgid, create_infobase_for_user, register_user, check_user_binding, update_user_data, choose_infobase

with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)



BOT_TOKEN = config['BOT_TOKEN']['KEY']

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
is_tested = False




@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    tg_id = message.from_user.id
    params = message.text.split()
    print(len(params))
    if len(params)==1:
        await message.reply('Нужен токен для запуска бота')
        return
    tg_token = params[1]
    tg_login = message.from_user.username

    if len(tg_token)==0:
        await message.reply('Необходимо указаить токен при запуске бота')
    print(tg_token)
    try:
        if not await check_user(tg_token):
            await message.reply("Пользователь не найден, у вас нет прав на работу с этим ботом")
        else:

            await update_user_info(tg_id, tg_login, tg_token)
    except Exception as e:
        await message.reply("Произошла ошибка!")
        pass


@dp.message(Command("create_infobase"))
async def cmd_create_infobase(msg: types.Message):
    #user_id, server_id, db_name, infobase_name, target_state, target_state_ts
    tgid = msg.from_user.id
    try:
        userid, login = await get_userid_login_by_tgid(tgid)
        dbname, infoname = await create_infobase_for_user(userid, login)
        await msg.reply(f'{dbname}, {infoname}')
        await bot.send_message()
    except Exception as e:
        await msg.reply(e)
        pass

    await msg.answer("Введите название информационной базы:")


@dp.message(Command("show_infobase"))
async def cmd_show_infobase(msg: types.Message):
    tgid = msg.from_user.id
    try:
        userid, login = await get_userid_login_by_tgid(tgid)
        dbases = await show_active_db(userid)
        print(dbases)
        dbases_str = '\n'.join(dbases)
        await msg.reply(dbases_str)
    except Exception as e:
        await msg.reply(e)
        pass

    await msg.answer("Введите название информационной базы:")

@dp.message(Command("turn_off_infobase"))
async def turn_off_infobase(message: types.Message):
    tg_id = message.from_user.id
    params = message.text.split()
    print(len(params))
    if len(params) < 2:
        await message.text("Слишком мало данных предоставлено")
        return
    Hostname = params[1]
    try:
        await turnoffinfobase(Hostname)
        await message.reply(f'{Hostname} turned off')
    except Exception as e:
        await message.reply("Error!")

@dp.message(Command("delete_infobase"))
async def delete_infobase(message: types.Message):
    tg_id = message.from_user.id
    params = message.text.split()
    print(len(params))
    if len(params) < 2:
        await message.text("Слишком мало данных предоставлено")
        return
    Hostname = params[1]
    try:
        await deleteinfobase(Hostname)
        await message.reply(f'{Hostname} deleted successfully')
    except Exception as e:
        await message.reply("Error!"+str(e))




# Запуск бота
if __name__ == '__main__':
    asyncio.run(dp.start_polling(bot))
