from imports import *

from Database import *
from Classifier import*
from Query import *
from Input import *
from Transaction import *
from Similarity import *
from Api import *

class Chatbot:
    def __init__(self):
        self.name = "\033[1;32m<Cobain>:\033[0m"
        #create database
        self.db = Database()
        #create classifiers
        self.intent = Classifier('intent')
        self.confirm = Classifier('confirm', analyzer='char_wb', ngram=(2,4))#single words, word-based analyzer not as robust
        self.smalltalk = Classifier('smalltalk')
        #create DTMs
        self.responses = Similarity('responses')
        self.qanda = Query('qanda')
        #create information retriever
        self.api = Api()
        self.userprompt = self.update_userprompt()
        #set the current user
        self.context = None

    def update_userprompt(self,update=False):
        self.uid, self.user_name, first = self.db.set_user()
        if update:
            #if changing mid-chat
            return f"\033[1;34m<{self.user_name}>: \033[0m"
            
        if first:
            #first user of the system does not need to login
            return f"\033[1;34m<{self.uid}>: \033[0m"

        #otherwise login
        return self.login()

    def login(self):
        #else remembers the previous user
        print(f"{self.name} Am I still talking to {self.user_name if self.user_name else self.uid}?")
        confirm = Input(input("\033[1;34mConfirm:\033[0m "))
        if self.confirm.intent(confirm())=='yes':
            self.db.login(self.uid)
            print(f"{self.name} Nice to see you again!")
        else:
            print(f"{self.name} Have we met before?")
            confirm = Input(input("\033[1;34mConfirm:\033[0m "))
            if self.confirm.intent(confirm())=='yes':
                self.uid=None
                while not self.uid:
                    print(f"{self.name} Please enter your unique ID.\nType \033[1;31mnew\033[22;39m to create an account.")
                    uid = Input(input("\033[1;34muID:\033[0m "))
                    if uid().lower()=='new':
                        self.uid, self.user_name= self.db.new_user()
                        print(f"{self.name} Nice to meet you!")
                        break
                    self.uid, self.user_name = self.db.login(uid())
                    if self.uid:
                        print(f"{self.name} Nice to see you again{' '+self.user_name if self.user_name else ''}!")
            else:
                self.uid, self.user_name= self.db.new_user()
                print(f"{self.name} Nice to meet you!")
        return f"\033[1;34m<{self.user_name if self.user_name else self.uid}>: \033[0m"

    def retrain(self):
        self.intent.train()
        self.confirm.train()
        self.smalltalk.train()
        self.responses.create_dt_matrix()
        self.qanda.create_dt_matrix()

    def __main__(self):
        try:
            #opening prompt
            print(f'''\n\033[3mType \033[1;31mexit\033[22;39m to leave the chat at any time.\n\033[0m''')
            print(f"{self.name} My name is Cobain, your concert booking AI assisant. How can I help you today?")
            user_input = Input(input(self.userprompt))
            while True:
                #main loop
                output=''#clear output
                #context management
                inputs = user_input.standardise()
                if user_input() == 'exit':
                    print(f"{self.name} Goodbye!")
                    break
                for i in inputs:
                    ui = Input(i)
                    intent = self.intent.intent(ui())
                    answer, doc, confidence = self.qanda.answer(ui())
                    #if confidence and confidence>0.8:
                        #skip the sections
                        #intent=None
                    #context tracking
                    if not intent and self.context:
                        intent=self.context
                    else: self.context=None #reset context if topic changes

                    if intent=='actionable':
                        pattern=r'''(?:.*?(?:can\s*you*)?(?:recommend\s*(?:(?:me\s*)?some\s*)?|some\s*))?(?P<music>([A-Za-z-]+\s*)+?\s*(?=music|band(?:s)?|$))'''
                        try:
                            match = re.search(pattern,ui(), re.IGNORECASE | re.VERBOSE).group('music')
                            if not match or match in ['music','bands','band']:
                                #first time in loop - clarify genre
                                output+="What music genre do you like?"
                                print(f"{self.name} {output}")
                                output=''#clear output
                                user_input = Input(input(self.userprompt))
                                if user_input()=='exit':
                                    break
                                match = re.search(pattern,user_input().lower(), re.IGNORECASE | re.VERBOSE).group('music')
                            if match:
                                print("...")#user feedback - loading
                                music = Music(match)
                                if music.find_artists():
                                    output+=f"Here are some {music()} artists:\n"
                                    for artist in music.find_artists():
                                        output+=f"{artist}\n"
                                else:
                                    #learning
                                    output+="Sorry, I don't know that genre."
                                    genre = user_input()
                                    print(f"{self.name} {output} What's an artist that is {genre}?")
                                    output=''
                                    user_input = Input(input(self.userprompt))
                                    if user_input() != 'exit':
                                        print(f"{self.name} So {user_input()} is {genre}?")
                                        confirm = Input(input(self.userprompt))
                                        if self.confirm.intent(confirm()) =='yes':
                                            genre = Music(genre)
                                            genre.update_df(user_input(),genre())
                                            output+='Thanks!'
                                        else:
                                            output+='Nevermind.'
                                #complete successfully
                                self.context=None
                            else:
                                output+="I can recommend you artists based on your favourite genre."
                                #complete unsuccessfully
                                self.context = 'actionable'
                        except: print(f"{self.name} Sorry, I got confused.")
                    
                    elif intent in ['greeting','smalltalk']:
                        if intent == 'greeting':
                            #adjusts the reponses to the time of day
                            greetings = ['Hi! ','Hello! ','Hi there! ']
                            now = datetime.now()
                            if 12-now.hour>0:
                                greetings.append('Good morning! ')
                            elif 18-now.hour>0:
                                greetings.append('Good afternoon! ')
                            else: greetings.append('Good evening! ')
                            output+=rnd.choice(greetings)
                        else:
                            #find subintent
                            if self.context:
                                intent='weather'
                            else: intent = self.smalltalk.intent(ui())
                            if intent in ['name','age']:
                                subject = ui.subject()
                                if subject == 'bot':
                                    response= self.responses.answer(ui())
                                    if response:
                                        output += response
                                    else: output += "I don't know!"
                                elif subject == 'user':
                                    info = self.db.get_info(self.uid,intent)
                                    if not info:
                                        output+=f"I don't know your {intent}, what is it?"
                                        update =True
                                    else:
                                        output+=f'Your {intent} is {info}. Would you like to change it?'
                                        print(f"{self.name} {output}")
                                        confirm = Input(input(self.userprompt))
                                        if self.confirm.intent(confirm()) =='no':
                                            print(f"{self.name} Ok.")
                                            output=''
                                        else:
                                            output = f'What do you want your {intent} to be?'
                                            update = True
                                    if update:
                                        print(f"{self.name} {output}")
                                        info = Input(input(self.userprompt))
                                        print(f"{self.name} Do you want me to set your {intent} to {info()}?")
                                        confirm = Input(input(self.userprompt))
                                        if self.confirm.intent(confirm()) =='yes':
                                            self.db.set_info(self.uid,intent,info())
                                            if intent=='name':
                                                output = f"Excellent, I'll call you {info()} from now on!"
                                            else: output = f"All done for you."
                                            self.userprompt = self.update_userprompt(True)
                                        else: output = 'Ok.'
                            elif intent =='datetime':
                                now = datetime.now()
                                if 'time' in ui.tokenize():
                                    output+=f"The time is {now.strftime('%H:%M')}. "
                                if 'day' in ui.tokenize():
                                    output += f"It's {now.strftime('%A')}. "
                                if 'month' in ui.tokenize():
                                    output += f"{now.strftime('%B')}. "
                                if 'year' in ui.tokenize():
                                    output += f"{now.strftime('%Y')}, time flies! "
                                if 'date' in ui.tokenize():
                                    suffix = 'th'
                                    if int(now.day/10)==1:
                                        pass
                                    elif now.day%10==1:
                                        suffix='st'
                                    elif now.day%10==2:
                                        suffix='nd'
                                    elif now.day%10==3:
                                        suffix='rd'
                                    output += f"It's {now.strftime('%A')}, the {now.day}{suffix} of {now.strftime('%B')}."
                            elif intent == 'weather':
                                place = ui.proper_noun()
                                while not place:
                                    print(f"{self.name} {output}Where are you looking for?")
                                    output=''#clear output
                                    user_input = Input(input(self.userprompt))
                                    if user_input()=='exit':
                                        break
                                    else: place = user_input()
                                try:
                                    location, weather = self.api.request_weather(place)
                                    output += f'''At the moment in {location} it's {weather['temperature']} degrees, but it feels like {weather['feelslike']}.'''
                                    if weather['precip']>0.5:
                                        output += f''' Bring an umbrella if you leave the house, there's a {int(weather['precip']*100)}% chance of rain!'''
                                    self.context=None
                                except:
                                    output = "Please enter a UK city."
                                    self.context='smalltalk'
                            else:
                                response = self.responses.answer(ui())
                                if response:
                                    output += response
                                else: output+= rnd.choice(['Can you be more specific?',"I don't like that topic.","Hmm...","I don't know enough about that."])
                    elif intent == 'transaction':
                        if os.path.exists(f'transactions/{self.uid}'):
                            transactions=[]
                            for file in os.listdir(f'transactions/{self.uid}'):
                                t = joblib.load(os.path.join(f'transactions/{self.uid}', file))
                                if not t.complete:
                                    transactions.append(t)
                            if transactions:
                                if len(transactions)==1:
                                    print(f"{self.name} You've already started a booking. Would you like to continue?")
                                    confirm = Input(input(self.userprompt))
                                    if self.confirm.intent(confirm()) =='no':
                                        t = Transaction()
                                    else: output+=t.details()
                                else:
                                    print(f"{self.name} You have unfinished bookings.")
                                    for idx, t in enumerate(transactions):
                                        print(f"{idx}: {t.details()}")
                                    print(f"{self.name} Would you like to continue?")
                                    confirm = Input(input(self.userprompt))
                                    if self.confirm.intent(confirm()) =='yes':
                                        print(f"{self.name} Which booking would you like to continue?")
                                        user_input = Input(input(self.userprompt))
                                        t = transactions[user_input()-1]
                                    else:
                                        output+="Ok. Starting a new booking."
                                        t= Transaction()
                            else:
                                output+="Let's find some tickets!\n"
                                t = Transaction()
                        else:
                            output+="Let's find some tickets!\n"
                            t = Transaction()
                        output+="\n\033[3mType \033[1;31mback\033[22;39m to go back a step.\nType \033[1;31mreset\033[22;39m to start again.\nType \033[1;31mcancel\033[22;39m to cancel booking.\nType \033[1;31mhelp\033[22;39m for help.\033[0m\n"
                        print(f"{self.name} {output}")
                        output=t.run(self)
                    elif confidence:
                        #3-tiered confidence
                        if confidence>0.5:
                            output+=answer
                        elif confidence>0.3:
                            #implicit confirmation
                            if doc:
                                output+= f"Are you asking about {doc}?"
                                print(f"{self.name} {output}")
                                confirm = Input(input(self.userprompt))
                                if self.confirm.intent(confirm()) =='yes':
                                    output = answer
                                else:
                                    output = "Sorry, I misunderstood you. How can I help you?"
                    else:
                        output+= "Sorry, I don't know about that. How can I help you?"
                if user_input()!='exit':
                    if output=='':
                        output+="How can I help you?"
                    print(f"{self.name} {output}")
                    user_input = Input(input(self.userprompt))
        finally: self.db.disconnect()