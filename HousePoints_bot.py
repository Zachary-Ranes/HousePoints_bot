#Author: Zachary Ranes
#Written in Python 2.7, requires eternnoir/pyTelegramBotAPI to run

import ConfigParser
import cPickle as pickle

import telebot
from telebot import types

from HousePoints_bot_Scores import School

#Read configure file
config = ConfigParser.ConfigParser()
config.read("Config.cfg")

#Associates bot with token 
bot = telebot.TeleBot(config.get("telegram_bot_api","telegram_token"))

#This dictionary holds an object for each chat (chat being a school) 
schools = {}

#key is a messages ID returns a users ID
messages_awaiting_responses = {}

#Loads scores from file when bots startup
try:
    schools = pickle.load(open("HousePoints_bot_Data.p", "rb"))
#The first time this bot runs this will fail so this bit is in a try
except: pass

#The first person in a chat that runs this command becomes headmaster
@bot.message_handler(commands=['start'])
def command_start(message):
    key = message.chat.id
    if key in schools:
        bot.reply_to(message, "There is already a school established here.")
    if message.chat.type == "private":
        bot.reply_to(message, "You can't start a school in a private chat.")
    if key not in schools and message.chat.type == "group"\
    or key not in schools and message.chat.type == "supergroup":
        schools[key] = School(message.from_user.id,
                              message.from_user.first_name,
                              message.from_user.last_name)
        pickle.dump( schools, open( "HousePoints_bot_Data.p", "wb" ) )
        bot.reply_to(message, "A new school has been formed in this chat "\
                              "with you as its headmaster.")
        
#Expected command for bots
@bot.message_handler(commands=['help'])
def command_help(message):
    bot.reply_to(message, "When someone runs the /start command in a chat for "\
                          "the first time a school if formed in that chat and "\
                          "the user that runs the command becomes the "\
                          "headmaster of the school. The headmaster can add "\
                          "a chat member as a prefect after they run the "\
                          "/prefect_test command with the /add_prefect command"\
                          ". The Headmaster can also remove prefects, add "\
                          "houses to the school and remove house from the "\
                          "school with the /school_settings command. The "\
                          "headmaster and prefect can award points to the "\
                          "houses with the /award_points command. Any member "\
                          "of the chat can run the /house_totals command "\
                          "to see the houses of the school and their points")

#Prefect logic will add the play to a list that the headmaster can approve
@bot.message_handler(commands=['prefect_test'])
def command_prefect_test(message):
    key = message.chat.id 
    if key in schools:
        output = schools[key].add_to_prefect_waiting_list(message.from_user.id,
                                                   message.from_user.first_name,
                                                   message.from_user.last_name)
        bot.reply_to(message, output)
        pickle.dump( schools, open( "HousePoints_bot_Data.p", "wb" ) )
    else:
        bot.reply_to(message, "There is not school in the chat.")

#Allows the headmaster to add player that have rung prefect test to the prefects
@bot.message_handler(commands=['add_prefect'])
def command_add_prefect(message):
    key = message.chat.id
    if key in schools:
        output = schools[key].review_prefect_waiting_list(message.from_user.id)
        bot.reply_to(message, output[0], reply_markup=output[1])
    else:
        bot.reply_to(message, "There is not school in the chat.")

#Callback for the adding of prefect from a list that is given to headmaster
@bot.callback_query_handler(func=lambda call: call.message.chat.id in schools 
                                                and call.data[0:24] == \
                                                "HousePoints_add_prefect_")
def callback_from_add_prefect(call):
    key = call.message.chat.id 
    output = schools[key].add_prefect(call.from_user.id,
                                      int(call.data[24:]))
    if output:
        pickle.dump( schools, open( "HousePoints_bot_Data.p", "wb" ) )
        bot.edit_message_text(output, 
                              message_id=call.message.message_id, 
                              chat_id=call.message.chat.id,
                              reply_markup=None)

#Responds with a list of house that the headmaster or prefect can give points to 
@bot.message_handler(commands=['award_points'])
def command_select_houese_to_award_points(message):
    key = message.chat.id
    if key in schools:
        output = schools[key].houses_to_award_points(message.from_user.id)
        bot.reply_to(message, output[0], reply_markup=output[1])
    else:
        bot.reply_to(message, "There is not school in the chat.")

#Callback that puts up a force reply to the player prompting for how many points 
@bot.callback_query_handler(func=lambda call: call.message.chat.id in schools 
                                                and call.data[0:28] == \
                                                "HousePoints_award_points_to_")
def callack_ask_how_many_points(call):
    key = call.message.chat.id 
    output = schools[key].how_many_points(call.from_user.id,
                                          call.data[28:])
    if output:
        bot.edit_message_text(call.data[28:], 
                              message_id=call.message.message_id, 
                              chat_id=call.message.chat.id,
                              reply_markup=None)
        sent_message = bot.send_message(key, output[0], reply_markup= output[1])
        messages_awaiting_responses[sent_message.message_id] = \
                                                    call.from_user.id

#Parses the force replay to add points to a house
@bot.message_handler(func=lambda message: message.chat.id in schools
                                      and message.reply_to_message != None)
def award_points_to_house(message):
    key = message.chat.id 
    if message.from_user.id \
    == messages_awaiting_responses[message.reply_to_message.message_id]:
      output = schools[key].add_points(message.from_user.id, message.text)
      del messages_awaiting_responses[message.reply_to_message.message_id]
      pickle.dump( schools, open( "HousePoints_bot_Data.p", "wb" ) )
      bot.reply_to(message, output[0], reply_markup=output[1])

#Shows all the houses in a school and their points 
@bot.message_handler(commands=['house_totals'])
def command_house_totals(message):
    key = message.chat.id 
    if key in schools:
        output = schools[key].house_totals()
        bot.reply_to(message, output)
    else:
        bot.reply_to(message, "There is not school in the chat.")

#Shows a schools info, like who is the headmaster and who the prefects are
@bot.message_handler(commands=['school_info'])
def command_school_info(message): 
    key = message.chat.id 
    if key in schools:
        output = schools[key].school_info()
        bot.reply_to(message, output)
    else:
        bot.reply_to(message, "There is not school in the chat.")
"""
#Command that can be run by headmaster to change settings of the school
@bot.message_handler(commands=['school_settings'])
def command_school_settings(message):
    key = message.chat.id
    if key in schools:   
        output = schools[key].school_settings(message.from_user.id)
        if output:
            try:
                bot.edit_message_text(output[0], 
                                      message_id=call.message.message_id, 
                                      chat_id=call.message.chat.id,
                                      reply_markup=output[1])
            except: pass
    else:
        bot.reply_to(message, "There is not school in the chat.")

#
@bot.callback_query_handler(func=lambda call: call.message.chat.id in schools 
                              and call.data == "HousePoints_point_reset")
def callback_school_settings_reset(call):
    key = message.chat.id
    output = schools[key].school_settings_reset(message.from_user.id)
    if output:
        try:
            bot.edit_message_text(output[0], 
                                  message_id=call.message.message_id, 
                                  chat_id=call.message.chat.id,
                                  reply_markup=output[1])
        except: pass

#
@bot.callback_query_handler(func=lambda call: call.message.chat.id in schools 
                            and call.data[0:24] == "HousePoints_point_reset_")
def callback_school_settings_reset_options(call):
    key = message.chat.id
    output = schools[key].school_settings_reset(message.from_user.id, 
                                                call.data[24:])
    if output:
        try:
            bot.edit_message_text(output[0], 
                                  message_id=call.message.message_id, 
                                  chat_id=call.message.chat.id,
                                  reply_markup=output[1])
        except: pass

#
@bot.callback_query_handler(func=lambda call: call.message.chat.id in schools 
                              and call.data == "HousePoints_remove_prefect")
def callback_school_settings_remove_prefect(call):
    key = message.chat.id
    output = schools[key].school_settings_remove_prefect(message.from_user.id)
    if output:
        try:
            bot.edit_message_text(output[0], 
                                  message_id=call.message.message_id, 
                                  chat_id=call.message.chat.id,
                                  reply_markup=output[1])
        except: pass

#
@bot.callback_query_handler(func=lambda call: call.message.chat.id in schools 
                           and call.data[0:27] == "HousePoints_remove_prefect_")
def callback_school_settings_remove_prefect_id(call):
    key = message.chat.id
    output = schools[key].school_settings_remove_prefect(message.from_user.id, 
                                                         call.data[27:])
    if output:
        try:
            bot.edit_message_text(output[0], 
                                  message_id=call.message.message_id, 
                                  chat_id=call.message.chat.id,
                                  reply_markup=output[1])
        except: pass

#
@bot.callback_query_handler(func=lambda call: call.message.chat.id in schools 
                              and call.data == "HousePoints_remove_house")
def callback_school_settings_remove_house(call):
    key = message.chat.id
    output = schools[key].school_settings_remove_house(message.from_user.id)
    if output:
        try:
            bot.edit_message_text(output[0], 
                                  message_id=call.message.message_id, 
                                  chat_id=call.message.chat.id,
                                  reply_markup=output[1])
        except: pass

#
@bot.callback_query_handler(func=lambda call: call.message.chat.id in schools 
                    and call.data[0:25] == "HousePoints_remove_house_")
def callback_school_settings_remove_house_id(call):
    key = message.chat.id
    output = schools[key].school_settings_remove_house(message.from_user.id, 
                                                         call.data[25:])
    if output:
        try:
            bot.edit_message_text(output[0], 
                                  message_id=call.message.message_id, 
                                  chat_id=call.message.chat.id,
                                  reply_markup=output[1])
        except: pass

#
@bot.callback_query_handler(func=lambda call: call.message.chat.id in schools 
                                    and call.data == "HousePoints_add_house")
def callback_school_settings_add_house(call):
    key = message.chat.id
    output = schools[key].school_settings_new_house_name(message.from_user.id)
    if output:
        messages_awaiting_responses[call.message.message_id] = \
                                                    call.from_user.id
        try:
            bot.edit_message_text(output[0], 
                                  message_id=call.message.message_id, 
                                  chat_id=call.message.chat.id,
                                  reply_markup=output[1])
        except: pass

#
@bot.message_handler(func=lambda message: message.chat.id in schools
                                      and message.reply_to_message.message_id \
                                        in messages_awaiting_responses)
def add_new_house_to_school():
    key = message.chat.id 
    if message.from_user.id \
    == messages_awaiting_responses[message.reply_to_message.message_id]:
      output = schools[key].add_house(message.from_user.id, message.text)
      del users_adding_points[message.reply_to_message.message_id]
      bot.reply_to(message, output[0], reply_markup=output[1])

#
@bot.callback_query_handler(func=lambda call: call.message.chat.id in schools 
                                    and call.data == "HousePoints_close_school")
def callback_school_settings_remove_house(call):
    key = message.chat.id
    output = schools[key].school_settings_close_school(message.from_user.id)
    if output:
        try:
            bot.edit_message_text(output[0], 
                                  message_id=call.message.message_id, 
                                  chat_id=call.message.chat.id,
                                  reply_markup=output[1])
        except: pass

#
@bot.callback_query_handler(func=lambda call: call.message.chat.id in schools 
                               and call.data == "HousePoints_close_school_sure")
def callback_school_settings_remove_house_id(call):
    key = message.chat.id
    output = schools[key].school_settings_remove_house(message.from_user.id)
    if output:
        try:
            bot.edit_message_text(output[0], 
                                  message_id=call.message.message_id, 
                                  chat_id=call.message.chat.id,
                                  reply_markup=output[1])
        except: pass

#write a function to reset points and the end of the month/week
"""
bot.polling()
