import telebot
import redis
token = '1632519088:AAEgTHHPS6bzGGAwKu8PzdfESYAXsQ3nJ6o'
bot = telebot.TeleBot(token, parse_mode=None)
r = redis.Redis(host='localhost', port=6379, db=0)

@bot.message_handler(commands=['add'])
def add(message):
	bot.send_message(message.chat.id, "Напишите новое место")

	@bot.message_handler(content_types=['text'])
	def send_welcome(message):
		bot.send_message(message.chat.id, message.text)

bot.polling()
# r.rpush(876, 'pasha')
# print(r.lrange(876, 0, -1)[0].decode())