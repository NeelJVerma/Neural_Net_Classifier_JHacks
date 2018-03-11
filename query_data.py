from pymongo import MongoClient
from keras.models import load_model
import sys

classifier = load_model('model.h5')

from sklearn.preprocessing import StandardScaler
import numpy as np
import codecs

client = MongoClient('173.255.230.88', 27017)
db = client.tweets
coll = db.tweet_data
data = list(coll.find({'handle': sys.argv[1]}))

w1 = 0
w2 = 0
w3 = 0

for point in data:
    w1 = point['weight1']
    w2 = point['weight2']
    w3 = point['weight3']

scaler = StandardScaler()

xtraincp = codecs.open('xtrain.txt', encoding='cp1252')
xtestcp = codecs.open('xtest.txt', encoding='cp1252')

weights = []

xtrain = np.loadtxt(xtraincp)
xtest = np.loadtxt(xtestcp)

array = np.array([w1, w2, w3])
xtest = np.vstack([xtest, array])

weights.append(array)

xtrain = scaler.fit_transform(xtrain)
xtest = scaler.transform(xtest)

print classifier.predict(scaler.transform(np.array([xtest[1,:]]))) > 0.5
print np.array([xtest[1,:]])
