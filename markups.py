from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


btnProfile = KeyboardButton('Профиль')
btnSub = KeyboardButton('Оформление подписки')
btnSettings = KeyboardButton('Техподдержка')
btn_category = KeyboardButton('Выбрать категорию')
btn_track = KeyboardButton('Выбрать фишки для отслеживания')
btn_test = KeyboardButton('Тест')

mainMenu = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
mainMenu.add(btnProfile, btnSub)
mainMenu.add(btnSettings, btn_category)
mainMenu.add(btn_track, btn_test)




sub_inline_markup = InlineKeyboardMarkup(row_width=2)
btnSubMonth = InlineKeyboardButton(text='Месяц - 150 рублей', callback_data="submonth")
btn_three_sub_month = InlineKeyboardButton(text='3 месяца - 350 рублей', callback_data='three_month_sub')
sub_inline_markup.add(btnSubMonth, btn_three_sub_month)

tech_pod = InlineKeyboardMarkup(row_width=2)
tech_pod.add(InlineKeyboardButton(text='Связаться с поддержкой', url='https://t.me/bio_tech_support_bot'))

