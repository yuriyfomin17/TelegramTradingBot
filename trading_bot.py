from telebot import types

from binance_trading_data_fetcher import fetch_trading_date_for_one_day_interval_from_binance
from file_processing_util import *
from helper_functions import *
from trading_algorithm import trading_session
from io import BytesIO
import telebot

matplotlib.use('Agg')
bot = telebot.TeleBot("PASTE_YOUR_BOT_TOKEN")
c1 = types.BotCommand(command='start', description='Start the Bot')
bot.set_my_commands([c1])
bot.infinity_polling(none_stop=True)

USER_INFO = {}


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, reply_markup=create_menu(), text="Trading Bot Started!")
    reset_trading_data(message.chat.id)


@bot.message_handler(content_types=['document'])
def handle_csv(message):
    if message.document.mime_type.lower() != 'text/csv':
        bot.reply_to(message, 'Please send a valid CSV file.')
        return

    telegram_file = bot.get_file(message.document.file_id)
    ifile = bot.download_file(telegram_file.file_path)
    file_string = str(ifile, 'utf-8')
    if not is_valid_csv_format(file_string):
        bot.reply_to(message, 'Please send a valid CSV file.')
        return
    chat_id = message.chat.id
    csv_trading_data = process_csv_file(file_string)
    financial_info, net_gain_array = trading_session(price_stats=csv_trading_data,
                                                     num_prices=len(csv_trading_data[OPEN_PRICE_KEY]),
                                                     initial_capital=USER_INFO[chat_id][INITIAL_CAPITAL_KEY],
                                                     stop_loss_percentage=USER_INFO[chat_id][
                                                         STOP_LOSS_PERCENTAGE_KEY])
    bot.reply_to(message, reply_markup=create_menu(), text=financial_info)
    graph_image = create_net_gain_graph(net_gain_array,
                                        csv_trading_data[TIMESTAMP_KEY],
                                        csv_trading_data[TIMESTAMP_KEY][0],
                                        csv_trading_data[TIMESTAMP_KEY][-1])
    bot.send_photo(chat_id=chat_id, photo=graph_image, reply_markup=create_menu())
    reset_trading_data(chat_id)


@bot.message_handler()
def handle_menu_buttons(message):
    user_message: str = message.text
    chat_id = message.chat.id
    if chat_id not in USER_INFO:
        reset_trading_data(chat_id)
    if message.text == DOWNLOAD_CSV_TEMPLATE_BUTTON:
        send_csv_template(message)
        return
    elif message.text == UPLOAD_TRADING_DATA_CSV_BUTTON:
        if is_valid_trading_info(USER_INFO[chat_id]):
            bot.reply_to(message, UPLOAD_TRADING_DATA_CSV_MESSAGE, reply_markup=create_menu())
        else:
            bot.reply_to(message, ENTER_TRADING_INFORMATION_MESSAGE)
            bot.reply_to(message, VALID_TRADING_INFORMATION_EXAMPLE_MESSAGE, reply_markup=create_menu())
        return
    elif message.text == TRADE_BUTTON:
        if is_valid_trading_info(USER_INFO[chat_id]):
            bot.reply_to(message, STARTING_TRADING_SESSION_MESSAGE)
            start_date = USER_INFO[chat_id][START_DATE_KEY]
            end_date = USER_INFO[chat_id][END_DATE_KEY]
            trading_data = fetch_trading_date_for_one_day_interval_from_binance(start_date, end_date)

            financial_info, net_gain_array = trading_session(price_stats=trading_data,
                                                             num_prices=len(trading_data[OPEN_PRICE_KEY]),
                                                             initial_capital=USER_INFO[chat_id][INITIAL_CAPITAL_KEY],
                                                             stop_loss_percentage=USER_INFO[chat_id][
                                                                 STOP_LOSS_PERCENTAGE_KEY])
            bot.send_message(chat_id=chat_id, text=financial_info, reply_markup=create_menu())
            graph_image = create_net_gain_graph(net_gain_array, trading_data[TIMESTAMP_KEY], start_date, end_date)
            bot.send_photo(chat_id=chat_id, photo=graph_image, reply_markup=create_menu())
            reset_trading_data(chat_id)
        else:
            bot.reply_to(message, ENTER_TRADING_INFORMATION_MESSAGE)
            bot.reply_to(message, VALID_TRADING_INFORMATION_EXAMPLE_MESSAGE, reply_markup=create_menu())
        return

    trading_information = convert_to_trading_information(user_message)
    if trading_information is None:
        bot.reply_to(message, ENTER_TRADING_INFORMATION_MESSAGE, reply_markup=create_menu())
        return
    else:
        USER_INFO[chat_id][INITIAL_CAPITAL_KEY] = trading_information[INITIAL_CAPITAL_KEY]
        USER_INFO[chat_id][STOP_LOSS_PERCENTAGE_KEY] = trading_information[STOP_LOSS_PERCENTAGE_KEY]
        USER_INFO[chat_id][START_DATE_KEY] = trading_information[START_DATE_KEY]
        USER_INFO[chat_id][END_DATE_KEY] = trading_information[END_DATE_KEY]
        bot.reply_to(message, VALID_TRADING_INFORMATION_MESSAGE, reply_markup=create_menu())


def create_menu():
    menu_markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    download_template_button = types.InlineKeyboardButton(DOWNLOAD_CSV_TEMPLATE_BUTTON)
    upload_trading_data_button = types.InlineKeyboardButton(UPLOAD_TRADING_DATA_CSV_BUTTON)
    simulate_binance_trading_session = types.InlineKeyboardButton(TRADE_BUTTON)
    menu_markup.add(upload_trading_data_button)
    menu_markup.add(download_template_button)
    menu_markup.add(simulate_binance_trading_session)
    return menu_markup


@bot.message_handler(commands=['template'])
def send_csv_template(message):
    template_data = ('OPEN,CLOSE,TIMESTAMP\n'
                     '39897.59,40084.88,1706054400000.0\n'
                     '40084.89,39961.09,1706140800000.0\n')

    template_io = BytesIO(template_data.encode('utf-8'))
    template_io.name = 'template.csv'
    bot.send_document(message.chat.id, template_io, reply_markup=create_menu())


def reset_trading_data(chat_id):
    USER_INFO[chat_id] = {
        INITIAL_CAPITAL_KEY: None,
        STOP_LOSS_PERCENTAGE_KEY: None,
        START_DATE_KEY: None,
        END_DATE_KEY: None
    }

