import tweepy
from mpi4py import MPI
import pymongo
import json
import time
import sys

class weather_data():
    def get_users(self,cursor):
        while True:
            try:
                yield cursor.next()
            except tweepy.TweepError:
                time.sleep(20)
    
    def scrapeData(self,username):
        #Variables that contains the user credentials to access Twitter API
        access_token = "806686525681528832-0AjC2SmbC5pNerZPGUhHX5uyqR8hpm8"
        access_token_secret = "GBPUNElOQmfShgrTEaSxPnvdHmSOaWpNblBpZ7TqRXoif"
        consumer_key = "gc4n03M6x4kbEBGQ5c6lFcooE"
        consumer_secret = "6VMbaPSvLUL7yVqJpn2a6kdddRd1cGMXEijliqBV0QpYzyEErO"
        # two levels of authentication for the twitter app
        auth = tweepy.OAuthHandler(consumer_key,consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        # creation of a tweepy obj
        api = tweepy.API(auth)
        # scrape a users timeline for the top 500 tweets, will include retweets
        stuff = api.user_timeline(screen_name=username, count=500, include_rts=True)
        #search for desired keywords in tweet
        keywords = {
                "abandoned": 2,
                "achy": 1,
                "afraid": 2,
                "agitated": 1,
                "agony": 4,
                "alone": 1,
                "antisocial": 2,
                "anxious": 2,
                "breakdown": 1,
                "brittle": 1,
                "broken": 1,
                "consumed": 2,
                "crisis": 1,
                "crushed": 2,
                "crying": 2,
                "defeated": 1,
                "desolate": 4,
                "upset": 1,
                "weak": 1,
                "withdrawn": 3,
                "woeful": 4,
                "sadness": 2,
                "trapped": 1,
                "upset,": 1,
                "weak": 1,
                "exhausted": 2,
                "hurt": 1,
                "miserable": 2,
                "I": 1,
                "me": 1,
                "myself": 1,
                "am" : 1,
        }
        words_contained = []
        weight_one = 0
        weight_two = 0
        found = 0
        total_words = []
        #array for storing tweet
        self.tweets = []
        # add url and text from tweet to tuple
        for status in stuff:
            #check for non ascii characters within text field
            text = ""
            for char in status.text:
                if ord(char) < 128:
                    text = text + char
            words = text.split()
            total_words += words
            for word in words:
                if word in keywords:
                    words_contained.append(word)
                    weight_one += keywords[word]
                    found += 1
        if found > 0:
            weight_two = float(found) / len(total_words)
        weight3 = (weight_one + weight_two) / 2
        outcome = None
        if weight_one > 69 and weight_two > 0.0225 and weight3 > 26:
            outcome = 1
        else:
            outcome = 0
            
        return (username,None,words_contained,weight_one,weight_two,weight3,outcome)

def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
    
    user_names = []

    client = pymongo.MongoClient("173.255.230.88",27017)
    db = client.tweets
    split_lis = [sys.argv[1]]
    avg = len(user_names) / 4
    last = 0
    while last < len(user_names):
        split_lis.append(user_names[last: last + avg])
        last += avg
    if rank == 0:
        comm.send(split_lis[0], dest=1)
    else:
        users = comm.recv(source=0)
        tweet = None
        for handle in users.split():
            print handle
            tweet = weather_data().scrapeData(handle)

            if tweet != None:
                db.tweet_data.save({
                    "handle": tweet[0],
                    "weight1": tweet[3],
                    "weight2": tweet[4],
                    "weight3": tweet[5],
                    "outcome": tweet[6]
                })
        print(str(rank) + " data saved")
        return
main()
