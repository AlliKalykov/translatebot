import sqlite3
from telebot import TeleBot
from telebot import types
from googletrans import Translator


from config import TOKEN

bot = TeleBot(TOKEN)

connect_db = sqlite3.connect('tgbot.sqlite3', check_same_thread=False)

def create_table_followers():
    cursor = connect_db.cursor() # создаем курсор, который позволяет делать запросы к БД
    # запрос на создание таблицы, если ее нет
    cursor.execute(
        ' \
            CREATE TABLE IF NOT EXISTS followers \
                (\
                    id INTEGER PRIMARY KEY,\
                    user_id INTEGER UNIQUE,\
                    first_name TEXT,\
                    last_name TEXT,\
                    username TEXT\
                )\
        '
    )
    connect_db.commit() # сохраняем изменения, которые мы внесли в БД
    cursor.close() # закрываем курсор, чтобы освободить ресурсы


def add_follower(user_id, first_name, last_name, username):
    try:
        cursor = connect_db.cursor()
        cursor.execute(
            ''' 
                INSERT INTO followers (user_id, first_name, last_name, username) 
                VALUES (?, ?, ?, ?) 
            ''',
            (user_id, first_name, last_name, username)
        )
        connect_db.commit()
        cursor.close()
        return True
    except sqlite3.IntegrityError:
        return False

def delete_follower(user_id):
    cursor = connect_db.cursor()
    cursor.execute('DELETE FROM followers WHERE user_id = ?', (user_id,))
    connect_db.commit()
    cursor.close()

@bot.message_handler(commands=['start'])
def start_message(message):
    follow = types.KeyboardButton(text='/follow')
    unfollow = types.KeyboardButton(text='/unfollow')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(follow)
    markup.add(unfollow)
    bot.send_message(message.chat.id, 'Бот запущен', reply_markup=markup)

@bot.message_handler(commands=['follow'])
def follow_user(message):
    flag = add_follower(message.chat.id, message.chat.first_name, message.chat.last_name, message.chat.username)
    if flag:
        bot.send_message(message.chat.id, 'You are now following the bot')
    else:
        bot.send_message(message.chat.id, 'You are already following the bot')

@bot.message_handler(commands=['unfollow'])
def unfollow_user(message):
    print(message.chat.id)
    delete_follower(message.chat.id)
    bot.send_message(message.chat.id, 'You are no longer following the bot')
    

@bot.message_handler(content_types=['text'])
def send_text(message):
    translator = Translator()
    result = translator.translate(message.text, dest='ru')
    bot.send_message(message.chat.id, result.text)


if __name__ == '__main__':
    create_table_followers()
    bot.polling(none_stop=True)
