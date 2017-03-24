#Author: Zachary Ranes
#Written in Python 2.7

import datetime 
import telebot
from telebot import types

#
class School(object):
    #Constructor for class 
    def __init__(self, chat_id, headmaster_id, headmaster_f, headmaster_l):
        self.school_chat_id = chat_id
        self.headmaster_id = headmaster_id
        self.headmaster_name = headmaster_f + " " + headmaster_l
        self.prefect_waiting_list = {}
        self.prefects = {}
        self.houses = {"Gryffindor":0, 
                       "Slytherin":0, 
                       "Ravenclaw":0, 
                       "Hufflepuff":0}
        self.user_awarding_points_to_house = {}
        self.monthly_reset = False
        self.current_month = None
        self.past_houses_scores = None

    #
    def add_to_prefect_waiting_list(self, user_id, user_first, user_last):
        if user_id == self.headmaster_id:
            return "The Headmaster does not need to be a prefect"
        if user_id in self.prefects:
            return "You are already a prefect"
        if user_id in self.prefect_waiting_list:
            return "You have already taken the prefect test, "\
                   "now you need to wait for the headmasters decision."
        name = ""
        if user_first: name = user_first
        if user_last: name = name + " " + user_last
        self.prefect_waiting_list[user_id] = name
        return "You have taken the prefect test, "\
               "now wait for the headmaster to review it"

    #
    def review_prefect_waiting_list(self, user_id):
        if user_id != self.headmaster_id:
            return ("Only the headmaster can add prefects", None)
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
        markup = types.ForceReply(selective=True)
        return(("How many points should be awarded to "+house_name+"?"), markup)

    #
    def add_points(self, user_id, points_text):
        #markup = types.ReplyKeyboardHide(selective=False)
        markup = None
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
        message += "This school's houses are: \n"
        for house_name in self.houses:
            message += house_name + "\n"
        return message

    #
    def school_settings(self, user_id):
        if user_id != self.headmaster_id:
            return ("Only the headmaster can edit the schools settings", None)
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton(
                            callback_data="HousePoints_settings_add_house",
                            text="Start new house"),
                   types.InlineKeyboardButton(
                            callback_data="HousePoints_settings_remove_house",
                            text="Close a house"))
        markup.row(types.InlineKeyboardButton(
                            callback_data="HousePoints_settings_remove_prefect",
                            text="Remove a prefect"),
                   types.InlineKeyboardButton(
                            callback_data="HousePoints_settings_reset_points",
                            text="Reset house points"))
        markup.row(types.InlineKeyboardButton(
                            callback_data="HousePoints_settings_close_school",
                            text="Close school"))
        return( "What would you like to change", markup)

    #
    def ask_new_house_name(self, user_id):
        if user_id != self.headmaster_id:
            return False
        markup = types.ForceReply(selective=True)
        return(("What is the name of the new house"), markup)

    #
    def add_house(self, house_name):
        #markup = types.ReplyKeyboardHide(selective=False)
        markup = None
        if house_name in self.houses:
            return("There is already a house by that name.", markup)
        self.houses[house_name] = 0
        return("The "+house_name+" house has been created.", markup)

    #
    def houses_to_remove(self, user_id):
        if user_id != self.headmaster_id:
            return False
        markup = types.InlineKeyboardMarkup()
        for house_name in self.houses:
            markup.row(types.InlineKeyboardButton(
                callback_data=("HousePoints_remove_house_"+house_name),
                text=house_name))
        return("Which house should be closed?", markup)

    #
    def remove_house(self, user_id, house_name):
        if user_id != self.headmaster_id:
            return False
        if house_name in self.houses:
            del self.houses[house_name]
            return "The house "+house_name+" has been closed."

    #
    def prefects_to_remove(self, user_id):
        if user_id != self.headmaster_id:
            return False
        markup = types.InlineKeyboardMarkup()
        for prefect_id in self.prefects:
            markup.row(types.InlineKeyboardButton(
                callback_data=("HousePoints_remove_prefect_"+str(prefect_id)),
                text=self.prefects[prefect_id]))
        return("Which prefect should be removed?", markup)

    #
    def remove_prefect(self, user_id, prefect_id):
        if user_id != self.headmaster_id:
            return False
        if prefect_id in self.prefects:
            name = self.prefects[prefect_id]
            del self.prefects[prefect_id]
            return name+" is no longer a prefect."

    #
    def reset_settings_info(self, user_id):
        if user_id != self.headmaster_id:
            return False
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton(
                            callback_data="HousePoints_reset_monthly",
                            text="Reset Monthly"),
                   types.InlineKeyboardButton(
                            callback_data="HousePoints_reset_never",
                            text="No Auto Reset"))
        markup.row(types.InlineKeyboardButton(
                            callback_data="HousePoints_reset_now",
                            text="Reset Points Now"))
        return("The bot can automatically reset the house's points at the "\
               "start of every month, you can also manually reset all the "\
               "house's points. Remember you can award negative points to "\
               "houses if you wish to remove points from a single house.", 
               markup)

    #
    def resset_settings(self, user_id, option):
        if user_id != self.headmaster_id:
            return False
        if option == "monthly":
            self.current_month = datetime.datetime.now().month
            self.monthly_reset = True
            return "The houses of this school will now have their points reset"\
                   " at the start of every month."
        if option == "never":
            self.current_month = None
            self.monthly_reset = False
            return "The houses of this school will not have their points reset."
        if option == "now":
            self.reset_house_scores()
            return "All houses have head their points reset to 0."

    #
    def check_for_point_reset(self, month):
        if self.monthly_reset:
            if month != self.current_month:
                self.reset_house_scores()
                return "Houses points have been reset."

    #
    def reset_house_scores(self):
        self.past_houses_scores = self.houses.copy()
        for house_name in self.houses:
            self.houses[house_name] = 0

    #
    def past_scores(self):
        if self.past_houses_scores == None:
            return "There has not been a point reset in this school yet."
        message = "Before the last reset the houses totals were:\n"
        for house_name in self.past_houses_scores:
            message += house_name + ": " + \
                str(self.past_houses_scores[house_name]) + "\n"
        return message


    def close_school(self, user_id, option=None):
        if user_id != self.headmaster_id:
            return False 
        if option == None:
            markup = types.InlineKeyboardMarkup()
            markup.row(types.InlineKeyboardButton(
                                callback_data="HousePoints_close_school_true",
                                text="Yes I am sure, Burn the school"),
                       types.InlineKeyboardButton(
                                callback_data="HousePoints_close_school_false",
                                text="No that was a mistake to click"))
            return("Headmaster ARE YOU SURE you want to close the school????", 
                    markup)
        if option == True:
            return ("The school in this chat is now GONE, an new headmaster "\
                    "can start a new school with the /start command.", None)
        if option == False:
            return ("Good the headmaster has come to their scenes.", None)
