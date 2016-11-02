#Author: Zachary Ranes
#Written in Python 2.7

import telebot
from telebot import types

#
class School(object):
    #Constructor for class 
    def __init__(self, headmaster_id, headmaster_first, headmaster_last):
        self.headmaster_id = headmaster_id
        self.headmaster_name = headmaster_first + " " + headmaster_last
        self.prefect_waiting_list = {}
        self.prefects = {}
        self.houses = {"Gryffindor":0, 
                       "Slytherin":0, 
                       "Ravenclaw":0, 
                       "Hufflepuff":0}
        self.user_awarding_points_to_house = {}

    #
    def add_to_prefect_waiting_list(self, user_id, user_first, user_last):
        if user_id == self.headmaster_id:
            return "The Headmaster does not need to be a prefect"
        if user_id in self.prefects:
            return "You are already a prefect"
        if user_id in self.prefect_waiting_list:
            return "You have already taken the prefect test, "\
                   "now you need to wait for the headmasters decision."
        self.prefect_waiting_list[user_id] = user_first + " " + user_last
        return "You have taken the prefect test, "\
               "now wait for the headmaster to review it"

    #
    def review_prefect_waiting_list(self, user_id):
        if user_id != self.headmaster_id:
            return "Only the headmaster can add prefects"
        markup = types.InlineKeyboardMarkup()
        for prefect_id in self.prefect_waiting_list:
            markup.row(types.InlineKeyboardButton(
                callback_data="HousePoints_add_prefect_"+str(prefect_id),
                text=self.prefect_waiting_list[prefect_id]))
        return("Who should be added as a prefect?", markup)

    #
    def add_prefect(self, user_id, prefect_id):
        if user_id != self.headmaster_id:
            return False
        self.prefects[prefect_id] = self.prefect_waiting_list[prefect_id]
        del self.prefect_waiting_list[prefect_id]
        return self.prefects[prefect_id] + " has been added as a prefect."

    #
    def houses_to_award_points(self, user_id):
        if user_id != self.headmaster_id and user_id not in self.prefects:
            return("Only the prefects and headmaster can award points", None)
        markup = types.InlineKeyboardMarkup()
        for house_name in self.houses:
            markup.row(types.InlineKeyboardButton(
                callback_data=("HousePoints_award_points_to_"+house_name),
                text=house_name))
        return("Which house would you like to award points to?", markup)

    #
    def how_many_points(self, user_id, house_name):
        if user_id != self.headmaster_id and user_id not in self.prefects:
            return False
        self.user_awarding_points_to_house[user_id] = house_name
        markup = types.ForceReply(selective=False)
        return(("How many points should be awarded to "+house_name+"?"), markup)

    #
    def add_points(self, user_id, points_text):
        markup = types.ReplyKeyboardHide(selective=False)
        try:
            points = int(points_text)
        except:
            del self.user_awarding_points_to_house[user_id]
            return("Invalid input, use digits not text", markup)
        house_name = self.user_awarding_points_to_house[user_id]
        del self.user_awarding_points_to_house[user_id]
        self.houses[house_name] += points
        return(str(points)+" point(s) have been awarded to "+house_name, markup)

    #
    def house_totals(self):
        message = ""
        for house_name in self.houses:
            message += house_name + ": " + str(self.houses[house_name]) +"\n"
        return message

    #
    def school_info(self):
        message = "This school's headmaster is:\n"+ self.headmaster_name +"\n"\
                  "This school's prefects are: \n" 
        for prefect_id in self.prefects:
            message += self.prefects[prefect_id] + "\n"
        message += "This school has the following houses: \n"
        for house_name in self.houses:
            message += house_name + "\n"
        return message


