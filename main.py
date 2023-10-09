import telebot
from telebot import types

# Bot key
bot = telebot.TeleBot("")

# TG ID
TELEGRAM_ID = ""

is_question_mode = False

name = ""
questions = {
    1: {
        "question_text": "📅 Когда будет проходить форум?",
        "answer_text": "Форум будет проходить с 03.11 по 05.11"
    },
    2: {
        "question_text": "🕐 Сколько дней будет длиться форум?",
        "answer_text": "Форум будет длиться 3 дня (с пятницы по воскресенье)"
    },
    3: {
        "question_text": "🏠 Где будет проходить форум?",
        "answer_text": "Форум будет проходить в конторе пароходства по адресу 25 Октября, 23а ст1"
    },
    4: {
        "question_text": "👥 Кто организатор форума",
        "answer_text": "AIESEC - это международная молодежная организация, присутствующая в более чем 120 "
                       "странах.\n\nAIESEC в Тюмени действует уже 6 лет, занимаясь организацией международных "
                       "стажировок, волонтерских проектов по России, а также проводя форумы и ивенты, направленные на "
                       "развитие молодежного лидерства и межкультурного понимания. "
    },
    5: {
        "question_text": "❔ Что это за форум?",
        "answer_text": "«Пчела 2.0» - мероприятия для digital-специалистов из IT и digital сфер"
    },
}


def main_menu():
    keyboard = types.InlineKeyboardMarkup()

    key_reg = types.InlineKeyboardButton(text='📝 Регистрация', callback_data='registration')
    keyboard.add(key_reg)
    key_question = types.InlineKeyboardButton(text='❓ Есть вопрос', callback_data='question')
    keyboard.add(key_question)
    key_group = types.InlineKeyboardButton(text='👥 Группа ВКонтакте', callback_data='group')
    keyboard.add(key_group)
    key_program = types.InlineKeyboardButton(text='📊 Программа форума', callback_data='programm')
    keyboard.add(key_program)

    return keyboard


@bot.message_handler(content_types=['text'])
def start(message):
    global is_question_mode
    if message.text.lower() == "/start":
        bot.send_message(message.from_user.id, "Привет, давай сначала познакомимся. Я - бот-помощник для форума "
                                               "«Пчела 2.0»! Как мне к тебе обращаться?")
        bot.register_next_step_handler(message, get_name)
    elif is_question_mode:
        bot.send_message(message.from_user.id, "Я тебя не понимаю. Выбери вариант из списка (кнопок)")
    else:
        bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши '/start'")


def get_name(message):
    global name
    name = message.text

    keyboard = types.InlineKeyboardMarkup()
    key_yes = types.InlineKeyboardButton(text='Да', callback_data='yes')
    keyboard.add(key_yes)

    question = "Хорошо, " + name + ". Продолжим?"

    bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    global is_question_mode
    is_question_mode = True

    if call.data == "yes":
        bot.send_message(call.message.chat.id, "С чем тебе нужна помощь?", reply_markup=main_menu())
        bot.delete_message(call.message.chat.id, call.message.message_id)

    elif call.data == "registration":
        bot.send_message(call.message.chat.id, "Регистрируйся на форум прямо сейчас: \n\nhttps://bit.ly/pchela_tmn")
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "С чем тебе нужна помощь?", reply_markup=main_menu())

    elif call.data == "group":
        bot.send_message(call.message.chat.id, "Подписывайся на нашу группу ВКонтакте! Там мы разыгрываем различные "
                                               "призы и публикуем самые свежие новости :) \n\nhttps://vk.com/pchela_tmn")
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "С чем тебе нужна помощь?", reply_markup=main_menu())

    elif call.data == "programm":
        bot.send_message(call.message.chat.id, "Программа форума находится в разработке...")
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "С чем тебе нужна помощь?", reply_markup=main_menu())

    elif call.data == "question":
        keyboard = types.InlineKeyboardMarkup()

        for question_id, question_data in questions.items():
            question_button = types.InlineKeyboardButton(text=question_data["question_text"],
                                                         callback_data=f'answer_{question_id}')
            keyboard.add(question_button)

        key_no_question = types.InlineKeyboardButton(text='Тут нет моего вопроса', callback_data='no_question')
        keyboard.add(key_no_question)

        bot.send_message(call.message.chat.id, "Выбери вопрос:", reply_markup=keyboard)

        bot.delete_message(call.message.chat.id, call.message.message_id)

    elif call.data.startswith("answer_"):
        question_id = call.data.split("_", 1)[1]
        question_data = questions.get(int(question_id))

        if question_data:
            answer_text = question_data["answer_text"]
        else:
            answer_text = "Извините, ответ на этот вопрос не найден."

        bot.send_message(call.message.chat.id, answer_text)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "С чем тебе нужна помощь?", reply_markup=main_menu())

    elif call.data == "no_question":
        bot.send_message(call.message.chat.id,
                         "Напиши свой вопрос сюда и я передам его команде организаторов (оффтоп будет игнорироваться).")
        bot.register_next_step_handler(call.message, handle_user_question)


def handle_user_question(message):
    user_question = message.text

    # Получаем информацию о пользователе
    user_info = get_user_info(message.from_user)

    # Отправка вопроса в личные сообщения Telegram
    send_telegram_message(user_question, user_info)

    bot.send_message(message.chat.id, "Спасибо за вопрос! Он передан команде организаторов и скоро будет рассмотрен. Вам напишет наш менеджер в личные сообщения")
    bot.send_message(message.chat.id, "С чем тебе нужна помощь?", reply_markup=main_menu())


def send_telegram_message(message_text, user_info):
    try:
        user_id = user_info["id"]
        username = user_info.get("username", "")
        first_name = user_info.get("first_name", "")
        last_name = user_info.get("last_name", "")

        # Составляем текст сообщения с информацией о пользователе и его вопросе
        user_info_text = f"Пользователь: @{username}\nID: {user_id}\nИмя: {first_name}\nФамилия: {last_name}\n\n"
        full_message_text = user_info_text + f"Вопрос: {message_text}"

        bot.send_message(TELEGRAM_ID, full_message_text)
        bot.send_message(Kristina_TG_ID, full_message_text)
    except Exception as e:
        print("Ошибка при отправке сообщения в личные сообщения Telegram:", e)


def get_user_info(user):
    user_info = {
        "id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name
    }
    return user_info


bot.polling(none_stop=True, interval=0)
