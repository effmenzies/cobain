from imports import *

from Api import *

class Music(Api):
    def __init__(self,music,type=None):
        #load dataset
        self.genre_df = joblib.load('music/genre_df.joblib')
        self.name = music.lower()
        #classification
        if type=='genre' or self.is_genre(music):
            self.type='genre'
        else:
            self.genre = self.find_genre()
            self.type='artist'

    def __call__(self):
        return self.name.title()
    
    #learning new data
    def update_df(self,artist,genre):
        row = {'artist':artist,'genre':genre}
        updated = pd.concat([self.genre_df, pd.DataFrame([row])], ignore_index=True)
        #overwrite data
        joblib.dump(updated,'music/genre_df.joblib')
        #update the data
        self.genre_df = updated
        return True
    
    def is_genre(self,music):
        genres = set(self.genre_df['genre'].values)
        if "-".join(music.lower().split()) in genres:
            return True
        return None

    def find_artists(self):
        genre = "-".join(self.name.split())
        artists = self.genre_df[self.genre_df['genre']==genre]['artist'].values
        if len(artists)>0:
            selection=set()
            counter=0
            while len(selection)<3 and counter<20:
                counter+=1
                a = Music(rnd.choice(artists))
                if a.has_shows():
                    selection.add(a())
            return selection
        return None

    def find_genre(self):
        genre = self.genre_df[self.genre_df['artist']==self.name]['genre'].values
        if genre:
            return genre[0]
        return None
    
    def find_similar(self):
        return self.genre_df[self.genre_df['genre']==self.genre]['artist'].values

    def rand_similar(self):
        similar = self.find_similar()
        return rnd.choice(similar)
    
    def has_shows(self):
        shows, artist_item = self.request_artist(self())
        if not shows or shows == 0:
            return None
        return shows, artist_item