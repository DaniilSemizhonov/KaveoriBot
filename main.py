import telebot
from telebot import types
from mg import get_map_cell
import config


bot = telebot.TeleBot(config.token)
cols, rows = 8, 8
startmarkup = types.ReplyKeyboardMarkup(resize_keyboard=True)
item1 = types.KeyboardButton("Играть в лабиринт")
startmarkup.add(item1)

keyboard = telebot.types.InlineKeyboardMarkup()
keyboard.row( telebot.types.InlineKeyboardButton('←', callback_data='left'),
			  telebot.types.InlineKeyboardButton('↑', callback_data='up'),
			  telebot.types.InlineKeyboardButton('↓', callback_data='down'),
			  telebot.types.InlineKeyboardButton('→', callback_data='right') )

maps = {}
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id,
                     "I'm - <b>{1.first_name}</b>".format(
                         message.from_user, bot.get_me()),
                     parse_mode='html', reply_markup=startmarkup)

@bot.message_handler(content_types=['text'])
def on_buttonClick(message):
	if message.text == 'Играть в лабиринт':
		bot.send_message(message.chat.id, "Переворачивай телефон", reply_markup=types.ReplyKeyboardRemove())

		map_cell = get_map_cell(cols, rows)

		user_data = {
			'map': map_cell,
			'x': 0,
			'y': 0
		}

		maps[message.chat.id] = user_data

		bot.send_message(message.from_user.id, get_map_str(map_cell, (0, 0)), reply_markup=keyboard)


def get_map_str(map_cell, player):
	map_str = ""
	for y in range(rows * 2 - 1):
		for x in range(cols * 2 - 1):
			if map_cell[x + y * (cols * 2 - 1)]:
				map_str += "⬛"
			elif (x, y) == player:
				map_str += "🔴"
			else:
				map_str += "⬜"
		map_str += "\n"

	return map_str

@bot.callback_query_handler(func=lambda call: True)
def callback_func(query):
	user_data = maps[query.message.chat.id]
	new_x, new_y = user_data['x'], user_data['y']

	if query.data == 'left':
		new_x -= 1
	if query.data == 'right':
		new_x += 1
	if query.data == 'up':
		new_y -= 1
	if query.data == 'down':
		new_y += 1

	if new_x < 0 or new_x > 2 * cols - 2 or new_y < 0 or new_y > rows * 2 - 2:
		return None
	if user_data['map'][new_x + new_y * (cols * 2 - 1)]:
		return None

	user_data['x'], user_data['y'] = new_x, new_y

	if new_x == cols * 2 - 2 and new_y == rows * 2 - 2:
		bot.edit_message_text( chat_id=query.message.chat.id,
							   message_id=query.message.id,
							   text="Вы выиграли", reply_markup=startmarkup)
		return None

	bot.edit_message_text( chat_id=query.message.chat.id,
						   message_id=query.message.id,
						   text=get_map_str(user_data['map'], (new_x, new_y)),
						   reply_markup=keyboard )

bot.polling(none_stop=False, interval=0)