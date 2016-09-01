#Written by Zachary Ranes
#Writen for Python 3.4

import configparser
import pickle
import datetime 
import telebot
from telebot import types

#read config file
config = configparser.ConfigParser()
config.read("HousePoints_bot_config.cfg")

#associate bot with token 
bot = telebot.TeleBot(config.get("telegram_bot_api","telegram_token"))

#array for holding house points
#Gryffindor, Slytherin, Ravenclaw, Hufflepuff
HousePoints = [0,0,0,0]

#reading in records from file when bot starts up
try:
	with open("HousePoints_bot_record.pickle","rb") as record:
		HousePoints = pickle.load(record)
	record.close()
except:
	print("No HousePoints_bot_record.pickle file found, new one will be made apone first points awarded")


#an array that holds last months scores and the month number from which those scores are from
LastMonthsPoints =[0,0,0,0,0]

#read =ing in records of last months points
try:
	with open("HousePoints_bot_record_lastMonth.pickle","rb") as record:
		LastMonthsPoints = pickle.load(record)
	record.close()
except:
	print("No HousePoints_bot_record_lastMonth.pickle file found")

	
# list of prefects telegram id are in the config file
prefects = [int(id) for id in config.get("prefects", "id").split(", ")]

#Step 4 is rest becoues 0-3 are the four houses indexs wich makes it easyest to have those as the other steps
userStep = {} 
for id in prefects: userStep[id] = 4


#Fuction that check to see if new month has turned yet
def DateCheck(message):
	if (int(datetime.datetime.now().day) == 1) and (LastMonthsPoints[4] != int(datetime.datetime.now().month)):
		try:
			with open("HousePoints_bot_record_lastMonth.pickle","wb") as newRecord:
				pickle.dump(HousePoints, newRecord)
			newRecord.close()
			
		except:
			print("Failed to save pasted scores to file")

	
	

#hiddin comand to check id to be added to prefect list
@bot.message_handler(commands=['prefect_test'])
def CheckID(message):
	bot.send_message(message.chat.id, "Here is the ID to be added to the prefect list " + str(message.from_user.id))
		
		
#Command for anyone to use to see how many points each house has
@bot.message_handler(commands=['house_totals'])
def PointsCount(message):
    bot.send_message(message.chat.id, "Gryffindor:  " + str(HousePoints[0]) + 
														 "\nSlytherin:  " + str(HousePoints[1]) + 
														 "\nRavenclaw:  " + str(HousePoints[2]) + 
														 "\nHufflepuff:  " + str(HousePoints[3]))


#Command for anyone to use to see last months point scores of each house
@bot.message_handler(commands=['last_month'])
def PointsCount(message):
    bot.send_message(message.chat.id, "Last months scores were \nGryffindor:  " + str(LastMonthsPoints[0]) + 
																							  "\nSlytherin:  " + str(LastMonthsPoints[1]) + 
																							  "\nRavenclaw:  " + str(LastMonthsPoints[2]) + 
																							  "\nHufflepuff:  " + str(LastMonthsPoints[3]))
	
	
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
	
	
#is numbers 2 becouse it is called from 1G, 1S, 1R, 1H
def Addpoints2(index, message):
	howMany = types.ForceReply(selective=True)
	if message.from_user.id in prefects:
		bot.reply_to(message, "How many points do you wish to award to " + str(HouseNames(index)) + "?", reply_markup=howMany)
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
@bot.message_handler(func=lambda message: message.from_user.id in prefects and userStep[message.from_user.id] == 0)
@bot.message_handler(func=lambda message: message.from_user.id in prefects and userStep[message.from_user.id] == 1)
@bot.message_handler(func=lambda message: message.from_user.id in prefects and userStep[message.from_user.id] == 2)
@bot.message_handler(func=lambda message: message.from_user.id in prefects and userStep[message.from_user.id] == 3)
def AddPoints3(message):
	try:
		index = userStep[message.from_user.id]
		HousePoints[index]+= int(message.text)
		
		with open("HousePoints_bot_record.pickle","wb") as newRecord:
			pickle.dump(HousePoints, newRecord)
		newRecord.close()
		
		bot.send_message(message.chat.id, message.text + " Points awarded to " + str(HouseNames(index)))

	except:
		bot.send_message(message.chat.id, "Sorry that is not valid input")

	userStep[message.from_user.id] = 4

	

while True:
	try:
		bot.set_update_listener(DateCheck)
		bot.polling()
	except:
		time.sleep(30)