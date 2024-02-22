import telebot
from io import BytesIO
from telebot import types
from file_processing_util import valid_csv_format, process_csv_file, CAPITAL_PORTIONS, OPEN, INITIAL_CAPITAL_USD
from trading_algorithm import trading_session

BOT_TOKEN = ""
DOWNLOAD_CSV_TEMPLATE = "⬇️Download CSV Template"
UPLOAD_TRADING_DATA = "💷Simulate trading session"

bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, reply_markup=create_menu(), text="Trading Bot Started!")


@bot.message_handler(content_types=['document'])
def handle_csv(message):
    if message.document.mime_type.lower() != 'text/csv':
        bot.reply_to(message, 'Please send a valid CSV file.')
        return

    telegram_file = bot.get_file(message.document.file_id)
    ifile = bot.download_file(telegram_file.file_path)
    file_string = str(ifile, 'utf-8')
    if not valid_csv_format(file_string):
        bot.reply_to(message, 'Please send a valid CSV file.')
        return
    trading_data_to_process = process_csv_file(file_string)
    financial_info = trading_session(price_stats=trading_data_to_process,
                                     num_prices=len(trading_data_to_process[OPEN]),
                                     initial_capital=trading_data_to_process[INITIAL_CAPITAL_USD],
                                     capital_division_ration=1.0 / trading_data_to_process[CAPITAL_PORTIONS])
    bot.reply_to(message, reply_markup=create_menu(), text=financial_info)


@bot.message_handler()
def handle_menu_buttons(message):
    if message.text == DOWNLOAD_CSV_TEMPLATE:
        send_csv_template(message)
    elif message.text == UPLOAD_TRADING_DATA:
        bot.reply_to(message, "Upload your trading data")


def create_menu():
    menu_markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    download_template_button = types.InlineKeyboardButton(DOWNLOAD_CSV_TEMPLATE, callback_data='handle_menu_buttons')
    upload_trading_data_button = types.InlineKeyboardButton(UPLOAD_TRADING_DATA, callback_data='handle_menu_buttons')
    menu_markup.add(upload_trading_data_button)
    menu_markup.add(download_template_button)
    return menu_markup


@bot.message_handler(commands=['template'])
def send_csv_template(message):
    template_data = ('OPEN,CLOSE,TIMESTAMP\n'
                     'value1,value2,value3\n'
                     'value1,value2,value3\n')

    template_io = BytesIO(template_data.encode('utf-8'))
    template_io.name = 'template.csv'
    bot.send_document(message.chat.id, template_io, reply_markup=create_menu())


c1 = types.BotCommand(command='start', description='Start the Bot')
bot.set_my_commands([c1])

bot.infinity_polling(none_stop=True)
