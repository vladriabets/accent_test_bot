import telepot
import time
import os
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from description import descriptions

# Настройки приложения и базы данных
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///user.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
# Импорт моделей для базы данных и создание таблиц
from models import User
db.create_all()
db.session.commit()

# Создание бота по токену, сохранённому в переменной окружения
TOKEN = os.environ.get('TOKEN')
bot = telepot.Bot(TOKEN)

@app.route('/')
def hello():
    return 'Hello!'

# Чтение вопросов из файла
questions = []
with open('questions.txt') as file:
    for line in file:
        questions.append(line)

# Чтение указаний к какой акцентуации засчитывать ответ из файла
answers = []
with open('answers.txt') as file:
    for line in file:
        answers.append(line)

# Функции - помощники:

def user_in_table(user_id):
    """Проверяет наличие пользователя с данным id в таблице"""
    if User.query.filter_by(id=user_id).first():
        return True
    else:
        return False

def add_user(user_id, name):
    """Добавляет нового пользователя в таблицу"""
    new_user = User(id=user_id, username=name)
    db.session.add(new_user)
    db.session.commit()

def key_max(d):
     """Возвращает ключ словаря с наибольшим значением"""
     v=list(d.values())
     k=list(d.keys())
     return k[v.index(max(v))]

# Фунуции - обработчики

def on_chat_message(msg):
    """Обработчик сообщений"""

    content_type, chat_type, chat_id = telepot.glance(msg)
    if not user_in_table(chat_id):
        add_user(chat_id, msg['from']['first_name'])
    if content_type == 'text':
        if msg['text'] == '/start':
            bot.sendMessage(chat_id,
            'Добро пожаловать! Я готов провести тестирование '+
            'на определение акцентуации личности. ' +
            'Вам будут предложены утверждения, касающиеся вашего характера. ' +
            'Вы можете выбрать один их двух ответов: ' +
            '«да» или «нет», других вариантов ответов нет. ' +
            'Отвечайте быстро, долго не  раздумывая. ' +
            'Здесь нет правильных и неправильных ответов. ' +
            'От вашей искренности зависит достоверность полученного вами результата.' +
            'Во избежание ошибок - не нажиайте на один ответ несколько раз.\n' +
            'Начнём?',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text='Начать тестирование', callback_data='Начать')],
                    [InlineKeyboardButton(text='Позже', callback_data='Позже')],
                       ]))


def on_callback_query(msg):
    """Обработчик ответов со встроенной клавиатуры"""

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Да', callback_data='Да'),
            InlineKeyboardButton(text='Нет', callback_data='Нет')],
               ])
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    question_number = User.query.filter_by(id=from_id).first().question_number

    if query_data == 'Начать':
        if question_number >= 88:
            bot.sendMessage(from_id, 'Проходить тестирование второй раз не имеет смысла. ' +
            'Лучше - посоветуйте пройти тест своим друзьям. ;-)')
        bot.sendMessage(from_id, questions[question_number], reply_markup=keyboard)
    elif query_data == 'Позже':
        bot.sendMessage(from_id, 'Когда будете готовы - просто отправьте мне /start')
    if query_data in ['Да', 'Нет']:
        # Вопросы, за которые засчитывается балл при ответе "Нет"
        no_plus_questions = [4, 11, 24, 30, 35, 45, 50, 52, 58, 64]
        if query_data == 'Да' and not question_number in no_plus_questions:
            answer = 1
        elif query_data == 'Нет' and question_number in no_plus_questions:
            answer = 1
        else:
            answer = 0
        # Прибавляем баллы за ответ к соответствующей акцентуации
        column = int(answers[question_number])
        if column == 1:
            User.query.filter_by(id=from_id).first().demostrative += (answer * 2)
        elif column == 2:
            User.query.filter_by(id=from_id).first().rigid += (answer * 2)
        elif column == 3:
            User.query.filter_by(id=from_id).first().pedantic += (answer * 2)
        elif column == 4:
            User.query.filter_by(id=from_id).first().excitable += (answer * 3)
        elif column == 5:
            User.query.filter_by(id=from_id).first().hyperten += (answer * 3)
        elif column == 6:
            User.query.filter_by(id=from_id).first().dysthymic += (answer * 3)
        elif column == 7:
            User.query.filter_by(id=from_id).first().alarming += (answer * 3)
        elif column == 8:
            User.query.filter_by(id=from_id).first().cyclosilicate += (answer * 3)
        elif column == 9:
            User.query.filter_by(id=from_id).first().exalted += (answer * 6)
        elif column == 10:
            User.query.filter_by(id=from_id).first().emotive += (answer * 3)
        # После того, как ответ зачситан - переходим к следующему вопросу
        User.query.filter_by(id=from_id).first().question_number += 1
        # Все вопросы пройдены
        question_number = User.query.filter_by(id=from_id).first().question_number
        if question_number == 88:
            bot.sendMessage(from_id, 'Вы ответили на все вопросы. Готовы увидеть результат?',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text='Показать результат', callback_data='Показать')]]))
        else:
            bot.sendMessage(from_id, questions[question_number], reply_markup=keyboard)

        bot.answerCallbackQuery(query_id, text='Следующий вопрос...')

    if query_data == 'Показать':
        accentuations = {}
        accentuations['Демонстративный'] = User.query.filter_by(id=from_id).first().demostrative
        accentuations['Застревающий'] = User.query.filter_by(id=from_id).first().rigid
        accentuations['Педантичный'] = User.query.filter_by(id=from_id).first().pedantic
        accentuations['Возбудимый'] = User.query.filter_by(id=from_id).first().excitable
        accentuations['Гипертимический'] = User.query.filter_by(id=from_id).first().hyperten
        accentuations['Дистимический'] = User.query.filter_by(id=from_id).first().dysthymic
        accentuations['Тревожный'] = User.query.filter_by(id=from_id).first().alarming
        accentuations['Циклотимный'] = User.query.filter_by(id=from_id).first().cyclosilicate
        accentuations['Экзальтированный'] = User.query.filter_by(id=from_id).first().exalted
        accentuations['Эмотивный'] = User.query.filter_by(id=from_id).first().emotive
        if not any([value for key, value in accentuations.items() if value > 12]):
            bot.sendMessage(from_id, 'У вас не выражена ни одна из акцентуаций.' +
            'Либо вы стараетесь показаться социально нормативной личностью. ' +
            'Обычно такие люди демонстрируют сниженную самокритичность, неискренни.' +
            'В этом случае данные о чертах вашего характера недостоверны.' +
            'Либо вы - человек, лишенный привлекательной индивидуальности, пассивный, ' +
            'эмоционально обедненный. Такой человек старается уединиться, быть неприметным, ' +
            'медлителен. Он вряд ли станет лидером в коллективе, предпринимателем или борцом ' +
            'за идеи. Но за него можно и не беспокоиться: он не отважится на интриги, ' +
            'авантюры, вряд ли резко проявит свои эмоции. Исследования позволяют утверждать, ' +
            'что у подобных людей могут возникнуть сложности в преодолении трудных жизненных обстоятельств.')
        elif not any([value for key, value in accentuations.items() if value > 17]):
            accent = key_max(accentuations)
            score = accentuations[accent]
            bot.sendMessage(from_id, 'У вас отсутствуют ярко выраженные акцентуации, ' +
            'но могут присутствовать некоторые черты, которые характеризует '
            + accent + ' тип личности. Вы набрали ' + str(score) + ' баллов.')
            bot.sendMessage(from_id, 'Описание данного типа личности:\n' +
            descriptions[accent])
        else:
            accents_list = [key for key, value in accentuations.items() if value > 17]
            score = accentuations[accents_list[0]]
            if len(accents_list) == 1:
                bot.sendMessage(from_id, 'У вас ярко выражена одна акцентуация - ' +
                accents_list[0] + ' тип личности. Вы набрали ' + str(score) + ' баллов.')
                bot.sendMessage(from_id, 'Описание вашей акцентуации:\n' +
                descriptions[accents_list[0]])
            else:
                accent1 = key_max(accentuations)
                score1 = accentuations[accent1]
                accentuations.pop(accent1)
                accent2 = key_max(accentuations)
                score2 = accentuations[accent2]
                bot.sendMessage(from_id, 'У вас ярко выражены несколько акцентуаций.' +
                'Вот описания двух наиболее выраженных:')
                bot.sendMessage(from_id, accent1 + ' тип - ' + str(score1) + ' баллов.\n' + descriptions[accent1])
                bot.sendMessage(from_id, accent2 + ' тип - ' + str(score2) + ' баллов.\n' + descriptions[accent2])

    db.session.commit()

# Запускает обработку обновлений бесконечным циклом
MessageLoop(bot, {'chat': on_chat_message,
                  'callback_query': on_callback_query}).run_as_thread()
while True:
    time.sleep(10)
