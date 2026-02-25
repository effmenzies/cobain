from imports import *

from Input import *
from Music import *

class Transaction:
    def __init__(self,music=None):
        self.queue=deque([('class',None),('admission',None),('number of tickets',None),('date',None),('location',None),('music',music)],maxlen=6)
        self.accessible=False
        self.complete=False
        self.id = self.code()

    def next(self):
        self.queue.rotate(1)

    def is_step_one(self):
        return self.queue[-1][0]=='music'
    
    def back(self):
        if self.is_step_one():
            return None
        self.queue.rotate(-1)
        return True

    def undo(self):
        current = self.queue[-1][0]
        self.queue.appendleft((current,None))
        self.queue.rotate(-1)
        return True

    def jump_to(self,stage):
        if self.is_step_one():
            self.queue.rotate(-1)
        while self.queue[-1][0]!=stage:
            if self.is_step_one():
                return None
            self.undo()
            self.back()
        return True
    
    def reset(self):
        if self.is_step_one():
            self.back()
        while not self.is_step_one():
            self.undo()
            self.back()
        self.undo()
        return True
    
    def add(self,info):
        self.queue.appendleft((self.queue[-1][0],info))
        return True
    
    def code(self):
        characters = string.ascii_letters + string.digits
        return ''.join(rnd.choices(characters, k=7))

    def save(self,bot):
        if os.path.exists(f'transactions/{bot.uid}'):
            joblib.dump(self, f'transactions/{bot.uid}/{self.id}.joblib')
        else:
            os.mkdir(f"transactions/{bot.uid}")
            joblib.dump(self,f'transactions/{bot.uid}/{self.id}.joblib')
        return True
    
    def to_dict(self):
        info = dict(self.queue)
        info['accessible'] = self.accessible
        info['complete'] = self.complete
        return info

    def month(self,month):
        months={1:'January',2:'February',3:'March',4:'April',5:'May',6:'June',7:'July',8:'August',9:'September',10:'October',11:'November',12:'December'}
        return months[month]
    
    def to_date(self,date):
        date=datetime.strptime(date[:10],'%Y-%m-%d')
        suffix = {1:'st',2:'nd',3:'rd'}
        return f'the {date.day}{suffix[date.day%10] if (date.day%10 in range(1,4) and int(date.day/10)!=1) else "th"} of {self.month(date.month)} ({date.year})'

    def details(self):
        output='So far you have selected '
        d = self.to_dict()
        if d['number of tickets']:
            output+=f"{d['number of tickets']} "
        if d['admission']:
            output+=f"{d['admission']} "
        if d['class']:
            output+=f"{d['class']} "
        output+="tickets to see:\n"
        if d['music']:
            output+=f"{d['music']}"
        if d['location']:
            output+=f" in {d['location']}"
        if d['date']:
            output+=f" on {self.to_date(d['date'])}"
        if d['accessible']:
            output+=f", you have accessible tickets"
        return output+'.\n'


    def summarise(self):
        d = self.to_dict()
        return f'''You are going to see {d['music']} in {d['location'].title()} on the {self.to_date(d['date'])}.
You have {d['admission']}, {d['class']} tickets.
You {'do' if self.accessible else "don't"} require {'accessible tickets' if d['number of tickets']>1 else 'an accessible ticket'}.'''
    
    def help(self):
        current = self.queue[-1][0]
        if current == 'music':
            output = "Write the name of the artist or a genre you would like to see, and I will see if there are any upcoming shows!"
        elif current == 'location':
            output = "Write the name of the city you would like to go to. Choose from the list of available events above."
        elif current == 'date':
            output = "Enter the date you would like to go.\nFor example: \033[3mThe one in March, 2025\033[0m"
        elif current == 'number of tickets':
            output = "Enter how many tickets you would like. The maximum number of tickets in one transaction is six."
        elif current == 'admission':
            output = "You can choose from general admission or seated tickets."
        elif current == 'class':
            output = "You can choose from VIP (back-stage access, signing and a private bar) or standard tickets."
        return output

    def explore_events(self, bot, artist):
        print(f"{bot.name} Searching...")
        shows,item = artist.has_shows()
        print(f"{artist()} has {shows} shows coming up.")
        events = item['events']
        output="They are playing "
        for idx, event in enumerate(events):
            output+=f"in {event['location']} on {self.to_date(event['date'])}"
            if idx==shows-2:
                output+=' and '
            else: output+=', '
        return output[:-2]+'.'+'\nWould you like to book?'
    
    def match(self,user_input, current):
        if current == 'music':
            pattern=r'''(?:.*?(?:like|some|see|go\s*to(?:\s*see)?)\s*(?:.*?(?:some))?\s*)?
            ((?P<genre>.*?)(?=\s*music)|(?P<artist>.*?)(?=$))'''
            #pattern=r'''(?:.*?\b(i|we)(?:'d|'ll|\b)\s*(?:will|would(?:\slike)?|want|like)?\s*(?:to\s*)?(?:go\s*(?:to\s*)?)?(?:see(?:\s*some)?)?\s*)?
            #((?P<music>.*?(?=$))|(?P<genre>.*?(?=music)))'''
        elif current == 'location':
            pattern=r'''(?:.*?(?:in|to|around)?)?\s*
            (?P<location>([A-Za-z]+)+?)?'''
        elif current == 'admission':
            pattern=r'''(?P<standing>(?:(stand(ing)?|stood(?:\s*up)?|floor|pit|general\s*(?:admission)?|crowd|arena)\s*))|
            (?P<seated>(?:(seat(ed|ing)?|s[ia]t(ting)?|reserved|allocated|assigned|chair(s)?|tier(ed)?)\s*))'''
        elif current == 'class':
            pattern=r'''(?P<VIP>(VIP|premium|back\s*stage|special|gold))|
            (?P<general>(normal|nothing|regular|general|standard))'''
        match = re.search(pattern,user_input, re.IGNORECASE | re.VERBOSE)
        if match:
            for group in match.groupdict():
                if match.group(group):
                    return match.group(group), group
        return None
    
    def match_date(self,user_input):
        pattern=r'''(?:.*?\b(?:go|book)?\s*(?:on\s*)?(?:the\s*(?:one\s*in\s*)?)?)?
(?P<day>(?!in)\b([0-2]?[0-9]|3[01])(?:st|nd|rd|th|/b))?\s*
(?:of|/|`.|-|in)?\s*
(?P<month>\b(0?[1-9]|1[0-2]|[A-Za-z]+)\b)?\s*
(?:in|/|`.|-)?\s*
(?P<year>\b\d{2,4}\b)?'''
        match = re.search(pattern,user_input, re.IGNORECASE | re.VERBOSE)
        date=''
        if match:
            for group in match.groupdict():
                if match.group(group):
                    date+=f'{match.group(group)} '
            return parser.parse(date,fuzzy=True,dayfirst=True).__str__()[:10]
        return None
    
    def map_number(self, user_input):
        numbers = {'one':'1','two':'2','three':'3','four':'4','five':'5','six':'6'}
        pattern=r'''(?:.*?I\s*(?:would\s*like|want)\s*(to\s*buy)?\s*)?
        (?P<number>\b([0-6]|[A-Za-z]+)(?=ticket(s)?|\b|$))\s*(?:.*?)'''
        match = re.search(pattern,user_input, re.IGNORECASE | re.VERBOSE)
        if match:
            n = match.group('number').lower()
            if n in numbers.keys():
                return int(numbers[n])
            elif n in numbers.values():
                return int(n)
        return None

    def run(self,bot):
        while not all([field[1] for field in self.queue]):#checks all fields are filled
            current = self.queue[-1]
            if current[1]:
                print(f"{bot.name} You've selected {current[0]} as {current[1]}. Would you like to change?")
                confirm = Input(input(bot.userprompt))
                if bot.confirm.intent(confirm()) =='yes':
                    self.undo()#clears the entry
                else: self.next()
            else:
                print(f"{bot.name} What {current[0]} would you like?")
                user_input = Input(input(bot.userprompt))
                if user_input() == 'cancel':
                    if not self.is_step_one():
                        print(f"{bot.name} Do you want to save your progress?")
                        confirm = Input(input(bot.userprompt))
                        if bot.confirm.intent(confirm()) =='yes':
                            self.save(bot)
                            return 'Transaction saved.'
                        else:
                            print(f"{bot.name} Are you sure you want to delete your progress?")
                            confirm = Input(input(bot.userprompt))
                            if bot.confirm.intent(confirm())=='yes':
                                return 'Transaction cancelled.'
                            else:
                                print(f"{bot.name} No worries!")
                    else: return 'Transaction cancelled.'
                elif user_input() == 'back':
                    if not self.back():
                        print(f"{bot.name} This is step one!")
                elif user_input() == 'reset':
                    self.reset()
                    print(f"{bot.name} Reset.")
                elif user_input() == 'help':
                    output = self.help()
                    print(f"{bot.name} {output}")
                else:
                    if current[0] == 'music':
                        if self.match(user_input(), current[0]):
                            try:
                                match, group = self.match(user_input(),current[0])
                                match = Music(match,group)
                                if match.type=='artist':
                                    artist = match
                                    if artist.has_shows():
                                        print(f"{bot.name} {self.explore_events(bot,artist)}")
                                        confirm = Input(input(bot.userprompt))
                                        if bot.confirm.intent(confirm()) =='yes':
                                            self.add(artist())
                                            shows, item = artist.has_shows()
                                            if len(item['events'])==1:#only one event autofill
                                                event = item['events'][0]
                                                self.add(event['location'])
                                                self.add(event['date'])
                                        else: print(f"{bot.name} Ok.")
                                    else:
                                        print(f"{bot.name} I'm sorry, {artist()} has no upcoming shows.")
                                else:
                                    genre = match
                                    print(f"{bot.name} Searching...")
                                    artists = genre.find_artists()
                                    if artists:
                                        output = f"Here are some artists in that genre with upcoming shows:\n"
                                        for x in artists:
                                            output+=f"{x}\n"
                                        output = output[:-1]+"."
                                        print(output)
                                    else:
                                        print(f"{bot.name} Sorry, I don't know anyone in that genre! What's an artist that is {genre()}?")
                                        user_input = Input(input(bot.userprompt))
                                        print(f"{bot.name} So {user_input()} is {genre()}?")
                                        confirm = Input(input(bot.userprompt))
                                        if bot.confirm.intent(confirm()) =='yes':
                                            genre.update_df(user_input(),genre())
                                            print(f"{bot.name} Thanks!")
                                        else:
                                            print(f"{bot.name} Nevermind.")
                            except: print(f"{bot.name} I don't recognise that artist.")
                        else: print(f"{bot.name} I didn't recognise that.")
                    elif current[0] == 'location':
                        artist = Music(self.to_dict()['music'])
                        if self.match(user_input(), current[0]):
                            match, group = self.match(user_input(),current[0])
                            shows,item = artist.has_shows()
                            events = item['events']
                            chosen_events=[]
                            for e in events:
                                if e['location'].lower()==match.lower():
                                    chosen_events.append(e) #if there are multiple shows in the same place
                            if chosen_events:
                                self.add(match.lower())
                                if len(chosen_events)==1:
                                    self.add(chosen_events[0]['date'])#also adds the date, skips the next step
                            else:
                                locations = "\n".join([e['location'] for e in item['events']])
                                print(f"{bot.name} Choose from\n{locations}")
                        else: print(f"{bot.name} I didn't recognise that.")
                    elif current[0] == 'date':
                        try:
                            if self.match_date(user_input()):
                                match = self.match_date(user_input())
                                shows,item = artist.has_shows()
                                events = item['events']
                                chosen_events=[]
                                for e in events:
                                    if e['date']==match:#given exact date
                                        self.add(match.lower())
                                    elif (e['date'][:7]==match[:7] or e['date'][5:7]==match[5:] or e['date'][5:7]==match[5:7]):#matches specific details
                                        chosen_events.append(e)
            
                                if chosen_events:
                                    if len(chosen_events)==1:
                                        self.add(chosen_events[0]['date'])
                                    else: print(f"{bot.name} Please be more specific with the date.")
                                else: print(f"{bot.name} There is no event then.")
                            else:
                                dates = "\n".join([self.to_date(e['date']) for e in events])
                                print(f"{bot.name} Choose from\n{dates}")
                        except:
                            dates = "\n".join([self.to_date(e['date']) for e in events])
                            print(f"{bot.name} Choose from\n{dates}")
                    elif current[0] == 'number of tickets':
                        if self.map_number(user_input()):
                            self.add(self.map_number(user_input()))
                        else:
                            print(f"{bot.name} Please enter how many tickets you would like. The maximum number of tickets in one transaction is six.")
                    elif current[0] == 'admission':
                        if self.match(user_input(), current[0]):
                            match, group = self.match(user_input(), current[0])
                            self.add(group)
                        else: print(f"{bot.name} Sorry, I didn't recognise that type of ticket. {self.help()}")
                    elif current[0] == 'class':
                        if self.match(user_input(), current[0]):
                            match, group = self.match(user_input(), current[0])
                            self.add(group)
                        else: print(f"{bot.name} Sorry, I didn't recognise that type of ticket. {self.help()}")
        print(f"{bot.name} Do you have any disabilities and require an accessible ticket?")
        confirm = Input(input(bot.userprompt))

        if bot.confirm.intent(confirm()) =='yes':
            self.accessible=True
        print(f"{bot.name} Please confirm your booking:\n{self.summarise()}\n\033[1;3m(yes/no)\033[0m\n")
        confirm = Input(input(bot.userprompt))
        if bot.confirm.intent(confirm()) =='yes':
            self.complete=True
            self.save(bot)
            return 'Booking complete.'
        else:
            print(f"{bot.name} Would you like to make a change to your booking?")
            confirm = Input(input(bot.userprompt))
            if bot.confirm.intent(confirm()) =='yes':
                print(f"{bot.name} What would you like to change?\n1. Music\t2. Location\t3. Date\t4. Quantity\t5. Admission\t6. Class\t7. Accessibiltiy")
                user_input = Input(input(bot.userprompt))
                if user_input() == 7:
                    self.accessible = not self.accessible
                else:
                    while True:
                        stages = {1:'music',2:'location',3:'date',4:'number of tickets',5:'admission',6:'class'}
                        try:
                            stage = stages[int(user_input())]
                            self.jump_to(stage)
                        except: print(f"{bot.name} Please enter a number.")
                        break
                    output=self.run(bot)
                    return output
            else:
                print(f"{bot.name} Would you like to save your progress?")
                confirm = Input(input(bot.userprompt))
                if bot.confirm.intent(confirm()) =='yes':
                    self.save(bot)
                    return 'Transaction saved.'
                else:
                    print(f"{bot.name} Are you sure you want to delete your progress?")
                    confirm = Input(input(bot.userprompt))
                    if bot.confirm.intent(confirm()) =='yes':
                        return 'Transaction cancelled.'