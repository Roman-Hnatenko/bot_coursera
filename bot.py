import telebot
import redis
import re
import os
from token_ import token_
REDIS_URL = os.getenv('REDIS_URL')

bot = telebot.TeleBot(token_, parse_mode=None)
r = redis.Redis(REDIS_URL)

text_start = """
Привет, вот что я умею:

/add - добавление нового места
/list - отображение добавленных мест
/reset - удалить все добавленные локации
"""


def save_data(chat_id, name_location,  photo_id, date):
	r.rpush(chat_id, name_location)
	r.rpush(name_location, photo_id, date)


@bot.message_handler(commands=['start'])
def send_welcome(message):
	bot.send_message(message.chat.id, text_start)


@bot.message_handler(commands=['add'])
def add(message):
	bot.send_message(message.chat.id, "Напишите название нового места")
	bot.register_next_step_handler(message, get_place)


@bot.message_handler(commands=['list'])
def get_place_list(message):
	list_place = r.lrange(message.chat.id, 0, -1)
	rez_dict = dict()
	for place in list_place:
		l = r.lrange(place, 0, -1)
		rez_dict[place.decode()] = [i.decode() for i in l]
	list_place = list(rez_dict.keys())

	bot.send_message(message.chat.id, 'Вы планируете побывать в таких местах:' if list_place else 'Вы еще ничего не добавили:)')
	for place in list_place:
		bot.send_message(message.chat.id, f'Место: {place}\nДата: {rez_dict[place][1]}')
		bot.send_photo(message.chat.id, rez_dict[place][0])


@bot.message_handler(commands=['reset'])
def reset(message):
	r.delete(message.chat.id)
	bot.send_message(message.chat.id, f'Все записи успешно удалены\nВы никуда не едете:(')


def get_place(message):
	name_location = message.text
	bot.send_message(message.chat.id, f"Отправьте фотографию места: {name_location}")
	bot.register_next_step_handler(message, get_photo, name_location)


def get_photo(message, name_location):
	try:
		photo_id = message.photo[len(message.photo) - 1].file_id

		bot.send_message(message.chat.id, f"Напишите дату планиремого посещения\nФормат(00-00-0000)")
		bot.register_next_step_handler(message, get_date, name_location, photo_id)
	except Exception as e:
		bot.send_message(message.chat.id, f"Мне нужна фотография. Попробуй  еще раз)")
		bot.register_next_step_handler(message, get_photo, name_location)


def get_date(message, name_location, photo_id):
	try:
		date = re.search(r"\d{2}-\d{2}-\d{4}", message.text)
		date = date.group(0)

		save_data(message.chat.id, name_location, photo_id, date)
		bot.send_message(message.chat.id, 'Новая локация успешно сохранена!')
	except Exception as e:
		bot.send_message(message.chat.id, f'Мне нужна планируема дата в правильном формате(00-00-0000).\n\nПопробуй  еще раз:)')
		bot.register_next_step_handler(message, get_date, name_location, photo_id)


@bot.message_handler(content_types=['text'])
def send_what_to_do(message):
	bot.send_message(message.chat.id, 'Выбери вначале команду')


bot.polling()

