#Written by Zachary Ranes

import pickle
import configparser
import telebot
from telebot import types

#read config file
config = configparser.ConfigParser()
config.read("HousePoints_bot_config.cfg")

#associate bot with token
bot = telebot.TeleBot(config['telegram_bot_api']['telegram_token'])

#array for holding house points
#Gryffindor, Slytherin, Ravenclaw, Hufflepuff
bot.HousePoints = [0,0,0,0]

#reading in records from file when bot starts up
try:
	with open("HousePoints_bot_record.pickle","rb") as record:
		bot.HousePoints = pickle.load(record)
except:
	print("No HousePoints_bot_record.pickle file found")

# list of prefects telegram id are in the config file
prefects = [int(id) for id in config.get("prefects", "id").split(", ")]
userStep = {}
for id in prefects:
	userStep[id] = 4
#Step 4 is rest becoues 0-3 are the four houses indexs wich makes it easyest to have those as the other steps

#hiddin comand to check id to be added to prefect list
@bot.message_handler(commands=['prefect_test'])
def CheckID(message):
	bot.send_message(message.chat.id, "Here is the ID to be added to the prefect list " + str(message.from_user.id))

#so names of houses can be called by their index
def HouseNames(houseIdex):
	if houseIdex == 0:
		return "Gryffindor"
	if houseIdex == 1:
		return "Slytherin"
	if houseIdex == 2:
		return "Ravenclaw"
	if houseIdex == 3:
		return "Hufflepuff"
	
#Command for anyone to use to see how many points each house has
@bot.message_handler(commands=['house_totals'])
def PointsCount(message):
    bot.send_message(message.chat.id, "Gryffindor:  " + str(bot.HousePoints[0]) +
									  "\nSlytherin:  " + str(bot.HousePoints[1]) +
									  "\nRavenclaw:  " + str(bot.HousePoints[2]) +
									  "\nHufflepuff:  " + str(bot.HousePoints[3]))


#The force reply for the next four commands
adding = types.ForceReply(selective=True)

#is numbers 2 becouse it is called from 1G, 1S, 1R, 1H
def Addpoints2(index, message):
	if message.from_user.id in prefects:
		bot.reply_to(message, "How many points do you wish to award to " + str(HouseNames(index)) + "?", reply_markup=adding)
		userStep[message.from_user.id] = index
	else:
		bot.send_message(message.chat.id, "Only prefects can award points")


#the four main comands of the bot
@bot.message_handler(commands=['points_gryffindor'])
def AddPoints1G(message):
	Addpoints2(0, message)

@bot.message_handler(commands=['points_slytherin'])
def AddPoints1S(message):
	Addpoints2(1, message)

@bot.message_handler(commands=['points_ravenclaw'])
def AddPoints1R(message):
	Addpoints2(2, message)

@bot.message_handler(commands=['points_hufflepuff'])
def AddPoints1H(message):
	Addpoints2(3, message)

#this handles the responce to the four comands
@bot.message_handler(func=lambda message: message.from_user.id in prefects and userStep[message.from_user.id] != 4)
def AddPoints3(message):
	try:
		index = userStep[message.from_user.id]
		bot.HousePoints[index]+= int(message.text)
		with open("HousePoints_bot_record.pickle","wb") as newRecord:
			pickle.dump(bot.HousePoints, newRecord)
		bot.send_message(message.chat.id, message.text + " Points awarded to " + str(HouseNames(index)))

	except:
		bot.send_message(message.chat.id, "Sorry that is not valid input")

	userStep[message.from_user.id] = 4

bot.polling()
