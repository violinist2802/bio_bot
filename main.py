import logging
import time
import datetime as datatime
import random
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types.message import ContentType
import markups as nav
from db import Database
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler


TOKEN = '6459487051:AAE_0npBWErxXDlxX4jS92S5xKEDXNv5r1o'
YOOTOKEN = '381764678:TEST:65789'


logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


db = Database('base.db')

def form_sort_query(priority_result):
    features_names = ['sleep', 'food', 'productivity', 'brain']
    sort_names = ['sleep', 'food', 'productivity', 'brain']
    for i, j in enumerate(features_names):
        if priority_result[i] == 0:
            sort_names.remove(j)
    random.shuffle(sort_names)

    count = 0
    sort_query = ''
    for i, j in enumerate(sort_names):
        sort_query += ',' * count + j + ' desc'
        count = 1
    return sort_query


def days_to_seconds(days):
    return days * 24 * 60 * 60


def time_sub_day(get_time):
    time_now = int(time.time())
    middle_time = int(get_time) - time_now

    if middle_time <= 0:
        return False
    else:
        dt = str(datatime.timedelta(seconds=middle_time))
        dt = dt.replace("days", "дней")
        dt = dt.replace("day", "день")
        return dt



async def daily_routine(bot: Bot):
    id_list = db.get_ids()
    for id in id_list:
        await daily_message(bot, id)

async def daily_message(bot: Bot, user_id):
    user_sub = time_sub_day(db.get_time_sub(user_id))
    if not user_sub:
        await bot.send_message(user_id, 'Оформите подписку чтобы получать фишки')
    else:
        if not db.get_10(user_id):
            await bot.send_message(user_id, 'Выберите категорию фишек в меню, которая вам интересна')
        else:
            if db.get_features_count_current(user_id) < 10:
                u_id, used_list, priority_result = db.get_priorities(user_id)
                sort_query = form_sort_query(priority_result)
                feature_id, feature, description, picture_url = db.daily_feature(user_id, used_list, sort_query)
                db.user_used_update(user_id, feature_id, used_list)
                feature_used_list = db.get_features_used_current(user_id)
                db.feature_used_update(user_id, feature_id, feature_used_list)

                if picture_url is not None:
                    await bot.send_photo(user_id, picture_url, caption=feature)
                    await bot.send_message(user_id, description)
                else:
                    await bot.send_message(user_id, feature + '\n' + description)
            else:
                if not db.get_21(user_id):
                    await bot.send_message(user_id, 'Выберите 5 фишек для отслеживания в течение 21 дня в меню')


                else:
                    if db.get_days_count(user_id)<21:
                        track = db.get_track(user_id)
                        features_list = db.get_track_features(user_id, track)
                        mess = ''
                        for i, j in enumerate(features_list, start=1):
                            mess += '\n' + str(i) + '. ' + str(j)
                        await bot.send_message(user_id, 'Не забудь сегодня про фишки ДЕНЬ '+str(db.get_days_count(user_id)+1)+':'+mess)
                        db.plus_days_count(user_id, db.get_days_count(user_id)+1)
                    else:
                        await bot.send_message(user_id, 'Закончилось отслеживание фишек, выберите новую категорию для получения новых фишек или оставьте старую')
                        db.reset_10(user_id)
                        db.reset_21(user_id)
                        db.reset_track(user_id)
                        db.reset_feature_current(user_id)
                        db.reset_days_count(user_id)
                        db.reset_track_flag(user_id)
                        db.reset_priorities(user_id)


scheduler = AsyncIOScheduler(timezone='Europe/Moscow')
scheduler.add_job(daily_routine, trigger='interval', seconds=3600, kwargs={'bot': bot})
scheduler.start()





@dp.message_handler(commands=['start'])
async def start(message: types.Message):

    if not db.user_exists(message.from_user.id):
        db.add_user(message.from_user.id)
        await bot.send_message(message.from_user.id, "Укажите ваш никнейм, чтобы создать профиль.")
    else:
        await bot.send_message(message.from_user.id, f"Привет, {message.from_user.username}", reply_markup=nav.mainMenu)


@dp.message_handler()
async def bot_message(message: types.Message):
    if message.chat.type == 'private':
        if message.text == 'Профиль':
            user_sub = time_sub_day(db.get_time_sub(message.from_user.id))
            if user_sub:
                user_sub = "\nПодписка: Заканчивается через " + str(user_sub)
            if not user_sub:
                user_sub = 'Подписка: Отсутствует. Нажмите кнопку "Оформление подписки", чтобы приобрести её'

            description = 'Это ваш профиль. '
            user_password = 'Ваш ID: ' + db.get_password(message.from_user.id)
            count_p = 'Количество использованных фишек: ' + str(0)
            await bot.send_message(message.from_user.id, description + "\n" + user_password + "\n" + user_sub + "\n" + count_p)

        elif message.text == 'Техподдержка':
            await message.answer(f'Нажмите на кнопку, чтобы связаться с техподдержкой', reply_markup=nav.tech_pod)

        elif message.text == 'Оформление подписки':
            await bot.send_message(message.from_user.id, "описание подписки", reply_markup=nav.sub_inline_markup)

        elif message.text == 'Выбрать категорию':
            if not db.get_10(message.from_user.id):
                db.set_priority_flag(message.from_user.id)
                await bot.send_message(message.from_user.id,
                                       'Выберите одну из категорий фишек: 1.Сон, 2.Еда, 3.Продуктивность, 4.Мозговая активность')
            else:
                categories = ['Сон', 'Еда', 'Продуктивность', 'Мозговая активность']
                user_id, used_list, priority_result = db.get_priorities(message.from_user.id)
                for i in priority_result:
                    if i == 1:
                        category = categories[i]
                await bot.send_message(message.from_user.id,
                                       'На этот месяц уже выбрана категория: ' + category)

        elif db.get_priority_flag(message.from_user.id):
            if message.text in ['1', '2', '3', '4']:
                db.set_priorities(message.from_user.id, message.text)
                categories = ['Сон', 'Еда', 'Продуктивность', 'Мозговая активность']
                await bot.send_message(message.from_user.id,
                                       'На этот месяц выбрана категория: ' + categories[int(message.text)-1])
                db.reset_priority_flag(message.from_user.id)
                db.set_10(message.from_user.id)
            else:
                await bot.send_message(message.from_user.id,
                                       'Выбери одну категорию 1, 2, 3 или 4!')

        elif message.text == 'Тест':
            await daily_message(bot, message.from_user.id)

        elif message.text == 'Выбрать фишки для отслеживания':
            if db.get_features_count_current(message.from_user.id) != 10:
                await bot.send_message(message.from_user.id,
                                       'Дождитесь получения 10 фишек за этот месяц')
            else:
                used = db.get_features_used_current(message.from_user.id)
                features_list = db.get_features_current(message.from_user.id, used)
                mess=''
                for i, j in enumerate(features_list, start=1):
                    mess += '\n' + str(i) + '. ' + str(j)
                db.set_track_flag(message.from_user.id)
                await bot.send_message(message.from_user.id, 'Укажите номера 5 фишек, которые хотите отслеживать, через запятую' + mess)

        elif db.get_track_flag(message.from_user.id):

            try:
                flag = 0
                for i in message.text.split(','):
                    if int(i) < 1 or int(i) > 10:
                        flag = 1

            except:
                await bot.send_message(message.from_user.id,
                                       'Ошибка ввода: нераспознанный формат ввода. Введите номера фишек через запятую')


            else:
                if flag == 1:
                    await bot.send_message(message.from_user.id,
                                           'Ошибка ввода: Введите номера фишек от 1 до 10 (пример: 1,2,4)')
                elif len(message.text.split(',')) < 3 or len(message.text.split(',')) >5:
                    await bot.send_message(message.from_user.id,
                                           'Введите от 3 до 5 фишек')
                else:
                    track=''
                    used = db.get_features_used_current(message.from_user.id)
                    for i in message.text.split(','):
                        track += ',' +used.split(',')[2*int(i)-1] + ','
                    db.set_track(message.from_user.id, track)
                    db.reset_track_flag(message.from_user.id)
                    await bot.send_message(message.from_user.id,
                                           'Данные фишки будут отслеживаться в течение 21 дня')
                    track = db.get_track(message.from_user.id)
                    features_list = db.get_track_features(message.from_user.id, track)
                    mess = ''
                    for i, j in enumerate(features_list, start=1):
                        mess += '\n' + str(i) + '. ' + str(j)
                    await bot.send_message(message.from_user.id, 'Не забудь сегодня про фишки ДЕНЬ '+str(db.get_days_count(message.from_user.id)+1)+':'+mess)
                    curr_count = db.get_days_count(message.from_user.id)
                    db.plus_days_count(message.from_user.id, curr_count + 1)
                    db.set_21(message.from_user.id)








        else:
            if db.get_signup(message.from_user.id) == "setpassword":
                if len(message.text) > 15:
                    await bot.send_message(message.from_user.id, "Пароль не должен превышать 15 символов")
                elif "/" in message.text or "`" in message.text:
                    await bot.send_message(message.from_user.id, "Вы ввели запрещенный символ")
                else:
                    db.set_password(message.from_user.id, message.text)
                    db.set_signup(message.from_user.id, "done")
                    await bot.send_message(message.from_user.id, "Профиль создан успешно!",
                                           reply_markup=nav.mainMenu)
            else:
                await bot.send_message(message.from_user.id,
                                       'Бот вас не понял. '
                                       'Если у вас возникла проблема, '
                                       'нажмите кнопку Техподдержка и вам обязательно помогут:)')


@dp.callback_query_handler(text="submonth")
async def submonth(call: types.CallbackQuery):
    await bot.delete_message(call.from_user.id, call.message.message_id)
    await bot.send_invoice(chat_id=call.from_user.id,
                           title="Оформление подписки",
                           description="Тестовое описание товара",
                           payload="month_sub",
                           provider_token=YOOTOKEN,
                           currency="RUB",
                           start_parameter="test_bot",
                           prices=[{"label": "Руб", "amount": "15000"}])


@dp.callback_query_handler(text="three_month_sub")
async def three_month_sub(call: types.CallbackQuery):
    await bot.delete_message(call.from_user.id, call.message.message_id)
    await bot.send_invoice(chat_id=call.from_user.id,
                           title="Оформление подписки",
                           description="Тестовое описание товара",
                           payload="three_month_sub",
                           provider_token=YOOTOKEN,
                           currency="RUB",
                           start_parameter="test_bot",
                           prices=[{"label": "Руб", "amount": "35000"}])


@dp.pre_checkout_query_handler()
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def process_pay(message: types.Message):
    if message.successful_payment.invoice_payload == "month_sub":
        time_sub = int(time.time()) + days_to_seconds(30)
        db.set_time_sub(message.from_user.id, time_sub)
        await bot.send_message(message.from_user.id, "Вам выдана подписка на месяц")
    elif message.successful_payment.invoice_payload == "three_month_sub":
        time_sub = int(time.time()) + days_to_seconds(90)
        db.set_time_sub(message.from_user.id, time_sub)
        await bot.send_message(message.from_user.id, "Вам выдана подписка на 3 месяца")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
