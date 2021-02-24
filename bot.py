import telebot
import redis
import re


token = '1632519088:AAEgTHHPS6bzGGAwKu8PzdfESYAXsQ3nJ6o'
bot = telebot.TeleBot(token, parse_mode=None)
r = redis.Redis(host='localhost', port=6379, db=0)

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
	bot.send_message(message.chat.id, "Напишите новое место")
	bot.register_next_step_handler(message, get_place)


@bot.message_handler(commands=['list'])
def get_place_list(chat_id):
	list_place = r.lrange(chat_id, 0, -1)

	for place in list_place:
		pass


def get_place(message):
	name_location = message.text
	bot.send_message(message.chat.id, f"Отправьте фотографию места: {name_location}")
	bot.register_next_step_handler(message, get_photo, name_location)


def get_photo(message, name_location):
	try:
		photo_id =  message.photo[len(message.photo) - 1].file_id
		# bot.send_photo(message.chat.id, f_id)

		bot.send_message(message.chat.id, f"Напишите дату планиремого посещения\nФормат(00-00-0000)")
		bot.register_next_step_handler(message, get_date, name_location, photo_id)
	except Exception as e:
		bot.send_message(message.chat.id, f"Мне нужна фотография. Попробуй  еще раз)")
		bot.register_next_step_handler(message, get_photo, name_location)


def get_date(message, name_location, photo_id):
	try:
		date = re.search(r"\d{2}-\d{2}-\d{4}", message.text)
		date = date.group(0)
		print(message.chat.id)
		save_data(message.chat.id, name_location, photo_id, date)
		bot.send_message(message.chat.id, 'Новая локация успешно сохранена!')
	except Exception as e:
		bot.send_message(message.chat.id, f"Мне нужна планируема дата в правильном формате(00-00-0000).\n\nПопробуй  еще раз:)")
		bot.register_next_step_handler(message, get_date, name_location, photo_id)


@bot.message_handler(content_types=['text'])
def send_what_to_do(message):
	bot.send_message(message.chat.id, 'Выбери вначале команду')


bot.polling()
# r.rpush(876, 'pasha')
# print(r.lrange(876, 0, -1)[0].decode())
