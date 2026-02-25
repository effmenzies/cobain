from imports import *

class Api:
    def __init__(self):
        pass

    def request_weather(self,city):
        query = city.title()
        with open('datasets/weather.json','r') as file:
            data = ijson.items(file,'locations.item')
            for item in data:
                if item['location'] == query:
                    return query, item.get('weather')
            return None,None


    def request_artist(self,artist):
        with open('datasets/concerts.json','r') as file:
            artists = ijson.items(file,'artists.item')
            for item in artists:
                if item['artist']['name']==artist.lower():
                    return item.get('upcoming_event_count'), item
            return None,None

'''
    #create weather dataset
    def uk_city(self):
        cities = ["London","Manchester","Birmingham","Leeds","Glasgow","Sheffield","Liverpool","Edinburgh","Bristol","Cardiff","Leicester","Coventry","Nottingham","Newcastle upon Tyne","Southampton","Reading","Portsmouth","Brighton","Plymouth","Derby","Stoke-on-Trent","Wolverhampton","Aberdeen","Norwich","Swansea","Oxford","Cambridge","York","Bath","Exeter","Luton","Milton Keynes","Sunderland","Peterborough", "Ipswich","Dundee","Worcester","Chester","Carlisle", "Chelmsford","Canterbury","Gloucester","Durham","Newport","Wrexham","Bangor",
        "Inverness","Stirling","Perth","Middlesbrough","Bolton","Blackpool","Bournemouth","Bradford","Huddersfield","Wakefield","Telford","Slough","Basildon","Derry","Lisburn","Newry","Colchester","Hastings","Eastbourne","Northampton","Swindon","Stevenage","Maidstone","Hemel Hempstead","High Wycombe","Woking","Guildford","Epsom","Ashford","Folkestone","Margate","Rochester","Basingstoke","Aylesbury","Banbury","Harlow","Grimsby","Scunthorpe","Worksop","Hartlepool","Stockton-on-Tees","Darlington","Barrow-in-Furness","Blackburn","Burnley","Preston","Lancaster",
        "Morecambe","Southport","Wigan"]
        return cities

    def write_json(self):
        json_file = {'locations':[]}
        for city in self.uk_city():
            location, weather = self.request_weather(city)
            weather['precip']= rnd.choice([0,0.2,0.4,0.6,0.8,1.0])
            json_file['locations'].append({"location":location,"weather":weather})
            print(city)
        with open('datasets/weather.json','w') as file:
            json.dump(json_file, file, indent=4)
        print('done')

    #creating dataset
    def rand_date(self):
        start = datetime(2025,2,1)
        end = datetime(2026,2,28)
        delta = end-start
        days = rnd.randint(0,delta.days)
        date = start + timedelta(days=days)
        return date.__str__()

    def rand_city(self):
        cities = ['London','Manchester','Birmingham','Glasgow','Liverpool','Leeds','Bristol','Newcastle upon Tyne','Sheffield','Edinburgh','Cardiff','Belfast','Nottingham','Brighton','Southampton','Aberdeen','Dundee','Norwich','Oxford','Cambridge','Leicester']
        return rnd.choice(cities)

    def write_json_2(self):
        df = joblib.load('music/genre_df.joblib')
        genres=['alt-rock','alternative','black-metal','bluegrass','blues','classical','country','dance','death-metal','deep-house','disco','drum-and-bass','dubstep','edm','electro','electronic','emo','folk','funk','garage','goth','grindcore','grunge','hard-rock','hardcore','hardstyle','heavy-metal','hip-hop','house','indie','indie-pop','jazz','metal','metalcore','pop','progressive-house','psych-rock','punk','punk-rock','r-n-b','reggae','reggaeton','rock','rock-n-roll','rockability','singer-songwriter','ska','soul','techno','trance']
        artists = df[df['genre'].apply(lambda x: x in genres)]['artist'].values
        json_file = {'artists':[]}
        for idx, artist in enumerate(artists):
            shows = rnd.randint(0,3)
            artist_info = {'artist':{'id':idx,'name':artist},'upcoming_event_count':shows,'events':[]}
            for _ in range(shows):
                event = {"location":self.rand_city(),"date":self.rand_date()}
                artist_info['events'].append(event)
            json_file['artists'].append(artist_info)
            print(artist)
        with open('datasets/concerts.json','w') as file:
            json.dump(json_file, file, indent=4)
        print('done')
        '''