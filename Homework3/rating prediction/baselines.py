import gzip
import numpy as np
from collections import defaultdict

def readGz(f):
  for l in gzip.open(f):
    yield eval(l)

data = list(readGz("train.json.gz"))
train = data[:100000]
validation = data[100000:]
### Rating baseline: compute averages for each user, or return the global average if we've never seen the user before

allRatings = []
userRatings = defaultdict(list)
ratings = {}
userBoughtItem = defaultdict(list)
itemBoughtByUser = defaultdict(list)
betaU = {}
betaI = {}

print "Reading data..."
for l in train:
    user,item,rating = l['reviewerID'],l['itemID'], l['rating']
    key = str(user) + "###" + str(item)
    ratings[key] = rating
    allRatings.append(rating)
    userBoughtItem[user].append(item)
    itemBoughtByUser[item].append(user)
    betaU[user] = 0
    betaI[item] = 0
print "done"

alpha = 1.0 * sum(allRatings[:100000]) / 100000
alpha = 0

iteration = 20
lamda = 1

for i in range(0, iteration):
	print alpha, betaU['U989129959'], betaI['I734011860']
 	# update alpha
	alpha = (sum(ratings.values()) - sum(betaU.values()) - sum(betaI.values()))/ len(train)
	# update betaU
	for key in betaU:
		relavantItems = userBoughtItem[key]
		betaU[key] =  sum((ratings[str(key) + "###" + str(e)] - (alpha + betaI[e])) for e in relavantItems) / (lamda + len(relavantItems))
	# update betaI
	for key in betaI:
		relavantUsers = itemBoughtByUser[key]
		betaI[key] = sum((ratings[str(e) + "###" + str(key)] - (alpha + betaU[e])) for e in relavantUsers) / (lamda + len(relavantUsers))

realvalue = []
prediction = []

for l in validation:
    user,item,rating = l['reviewerID'],l['itemID'], l['rating']
    key = str(user) + "###" + str(item)
    realvalue.append(rating)
    bu = 0
    bi = 0
    if user in betaU:
    	bu = betaU[user]
    if item in betaI:
    	bi = betaI[item]
    prediction.append(alpha + bu + bi) 

def mse(a, b):
	c = np.subtract(a, b)
	c = c ** 2
	return np.sum(c) / len(c)

print mse(np.array(realvalue), np.array(prediction))