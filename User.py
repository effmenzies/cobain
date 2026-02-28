from imports import *

from Database import *
from Classifier import*
from Query import *
from Input import *
from Transaction import *
from Similarity import *
from Api import *

class User:
    def __init__(self, bot):
        # connect to the database
        self.db = Database()
        # instance of the bot
        self.bot = bot

        # load intent classifier
        self.confirm = Classifier('confirm', analyzer='char_wb', ngram=(2,4))

        # identify previous user
        self.username, self.name = self.db.last_user()

        # prompt
        self.prompts = Input()

    def prompt(self, text):
        self.prompts.process(text)

    def output(self, message):
        print(f"{self.bot.botprompt} {message}")

    def verify_user(self):
        if self.username:
            self.output(f"Is this still {self.username}?")
            response = input("Confirm: ")
            if self.confirm.intent(response) == 'yes':
                return True
        return False

    def login(self):
        if self.verify_user():
            # previous user exists & is confirmed
            username, name = self.db.login(self.username)
            self.output("Nice to see you again!")
            return username, name
        else:
            # different / new user
            self.output("Have we met before?")
            response = input("Confirm: ")
            if self.confirm.intent(response) == 'yes':
                while True:
                    self.output("Enter your username: ")
                    username = input("> ")
                    self.username, self.name = self.db.login(username)
                    if self.username:
                        self.output("Welcome back!")
                        return self.username, self.name
                    else:
                        self.output("I don't recognise that username. Would you like to create an account?")
                        response = input("Confirm: ")
                        if self.confirm.intent(response) == 'yes':
                            break
            self.output("Let's create an account for you. What would you like your username to be?")
            username = input("Username: ")
            while self.db.exists(username):
                suggestion = self.db.gen_username(username)
                self.output(f"That username is taken, please choose another.\nExample: {suggestion}")
                username = input("Username: ")
            self.username, self.name = self.db.new_user(username)
            self.output(f"Nice to meet you!")
            return self.username, self.name

    def retrain(self):
        self.intent.train()
        self.confirm.train()
        self.smalltalk.train()
        self.responses.create_dt_matrix()
        self.qanda.create_dt_matrix()