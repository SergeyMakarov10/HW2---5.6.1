import telebot
from telebot import types
from Config import TOKEN
from Extentions import APIException, Converter, currency


def create_markup(hid=None):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    buttons = []
    for symbol in currency:
        if symbol != hid:
            buttons.append(types.KeyboardButton(symbol.upper()))
    markup.add(*buttons)
    return markup


def commands_markup():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    buttons = ['/convert', '/values', '/help']
    markup.add(*buttons)
    return markup


bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start', 'help'])
def support_message(message: telebot.types.Message):
    text = "Бот осуществляет конвертации из одной валюты в другую на последнюю доступную дату.\n\n" \
           "Для конверации воспользуйтесь командой /convert или напишите сообщение боту в следующем формате:\n\n" \
           "<имя валюты> " \
           "<в какую валюты вы хотите перевести> " \
           "<количество переводимой валюты> \n\n" \
           "Доступные команды:\n" \
           "/convert - конвертация\n" \
           "/values - список доступных валют\n" \
           "/help - помощь"
    bot.reply_to(message, text, reply_markup=commands_markup())


@bot.message_handler(commands=['values'])
def available_curr(message: telebot.types.Message):
    text = "Доступные валюты:"
    keys = list(currency.keys())
    keys_per_row = 5
    curr = ""
    for i in range(0, len(keys), keys_per_row):
        keys_to_print = keys[i:i + keys_per_row]
        keys_row = '   '.join(keys_to_print)
        curr += keys_row + '\n'
    text = f"{text}\n{''.join(curr)}"
    bot.reply_to(message, text, reply_markup=commands_markup())


@bot.message_handler(commands=['convert'])
def convert(message: telebot.types.Message):
    text = 'Выберите валюту для конвертации:'
    bot.send_message(message.chat.id, text, reply_markup=create_markup())
    bot.register_next_step_handler(message, from_handler)


def from_handler(message: telebot.types.Message):
    quote = message.text
    text = 'Выберите валюту в которую конвертировать:'
    bot.send_message(message.chat.id, text, reply_markup=create_markup(hid=quote))
    bot.register_next_step_handler(message, to_handler, quote)


def to_handler(message: telebot.types.Message, quote):
    base = message.text
    text = 'Напишите количество конвертируемой валюты:'
    bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(message, amount_handler, quote, base)


def amount_handler(message: telebot.types.Message, quote, base):
    amount = message.text.strip()
    try:
        total_base = Converter.get_price(quote, base, amount)
    except APIException as e:
        bot.send_message(message.chat.id, f'Ошибка в конвертации:\n{e}')
    else:
        res = '{:,.2f}'.format(total_base)
        answer_text = f'Цена {amount} {quote.upper()} в {base.upper()} - {res}'
        bot.send_message(message.chat.id, answer_text, reply_markup=commands_markup())


@bot.message_handler(content_types=['text', ])
def convert(message: telebot.types.Message):
    try:
        values = message.text.split(' ')

        if len(values) != 3:
            raise APIException("Неверное количество параметров.")

        quote, base, amount = values
        total_base = Converter.get_price(quote, base, amount)
    except APIException as e:
        bot.reply_to(message, f'Ошибка пользователя.\n{e}')
    except Exception:
        bot.reply_to(message, f'Не удалось обработать команду. Пожалуйста, проверьте формат введенных валют.'
                              f'\nПример формата валют - eur, rub, usd'
                              f'\nВсе доступные валюты - /values.')
    else:
        res = '{:,.2f}'.format(total_base)
        text = f'Цена {amount} {quote.upper()} в {base.upper()} - {res}'
        bot.send_message(message.chat.id, text)


bot.polling(none_stop=True)
