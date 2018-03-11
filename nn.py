from pymongo import MongoClient
import csv
import numpy as np
import pandas as pd
import random

client = MongoClient('173.255.230.88', 27017)
db = client.tweets
coll = db.tweet_data
data = coll.find({}).limit(200000)

with open('data.csv', 'wb') as f:
    fields = ['handle', 'weight 1', 'weight 2', 'weight 3', 'outcome']
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()

    for point in data:
        w.writerow({'handle': point['handle'], 'weight 1': point['weight1'],
                'weight 2': point['weight2'], 'weight 3': point['weight3'], 'outcome': point['outcome']})

dataset = pd.read_csv('data.csv')

x = dataset.iloc[:, 1: 4].values
y = dataset.iloc[:, 4].values

from sklearn.model_selection import train_test_split

xtrain, xtest, ytrain, ytest = train_test_split(x, y, test_size=0.2, random_state=0)

from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
xtrain = scaler.fit_transform(xtrain)
xtest = scaler.transform(xtest)

np.savetxt('xtrain.txt', xtrain)
np.savetxt('xtest.txt', xtest)

import keras
from keras.models import Sequential
from keras.layers import Dense

classifier = Sequential()

classifier.add(Dense(units=2, kernel_initializer='uniform', activation='sigmoid', input_dim=3))
classifier.add(Dense(units=2, kernel_initializer='uniform', activation='sigmoid'))
classifier.add(Dense(units=2, kernel_initializer='uniform', activation='sigmoid'))
classifier.add(Dense(units=1, kernel_initializer='uniform', activation='sigmoid'))
classifier.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

classifier.fit(xtrain, ytrain, batch_size=10, epochs=20)

classifier.save('model.h5')

ypred = classifier.predict(xtest)
ypred = ypred > 0.5

from sklearn.metrics import confusion_matrix

matrix = confusion_matrix(ytest, ypred)
