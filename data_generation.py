from pymongo import MongoClient
from random import *
from mpi4py import MPI

def DB_connection():
    client = MongoClient('173.255.230.88',27017)
    db = client.tweets
    coll = db.tweet_data
    return coll

def get_twitter_data():
    coll = DB_connection()
    tweets = list(coll.find({}))
    for tweet in tweets:
        scalar1 = randint(1,10)
        scalar2 = uniform(.01,.02)
        scalar3 = randint(1,6)

        tweet['weight1'] = float(tweet['weight1'])
        tweet['weight2'] = float(tweet['weight2'])
        tweet['weight3'] = float(tweet['weight3'])

        tweet['weight1'] += scalar1 * choice([1,-1])
        tweet['weight2'] += scalar2 * choice([1,-1])
        tweet['weight3'] += scalar3 * choice([1,-1])
        if tweet['weight1'] > 69 and tweet['weight2'] >0.0225 and tweet['weight3'] > 26:
            tweet['outcome'] = 1
        else:
            tweet['outcome'] = 0
        del tweet['_id']
    return tweets

def save_tweet_data():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    coll = DB_connection()
    tweet_data = get_twitter_data()
    loadBalance = []
    avg = len(tweet_data) / 4 # 4 nodes in the cluster
    last = 0
    while last < len(tweet_data):
        loadBalance.append(tweet_data[last:last + avg])
        last += avg
    if rank == 0:
        comm.send(loadBalance[0], dest=1)
        comm.send(loadBalance[1], dest=2)
        comm.send(loadBalance[2], dest=3)
        comm.send(loadBalance[3], dest=4)
    else:
        tweets = comm.recv(source=0)
        for tweet in tweets:
            try:
                coll.insert(tweet)
            except:
                print "error while updating"
        print "update complete"

save_tweet_data()
