import numpy
import urllib
import scipy.optimize
import random
from math import exp
from math import log

random.seed(0)

def parseData(fname):
  for l in urllib.urlopen(fname):
    yield eval(l)

print "Reading data..."
dataFile = open("winequality-white.csv")
header = dataFile.readline()
fields = ["constant"] + header.strip().replace('"','').split(';')
featureNames = fields[:-1]
labelName = fields[-1]
lines = [[1.0] + [float(x) for x in l.split(';')] for l in dataFile]
X = [l[:-1] for l in lines]
y = [l[-1] > 5 for l in lines]
print "done"

def inner(x,y):
  return sum([x[i]*y[i] for i in range(len(x))])

def sigmoid(x):
  return 1.0 / (1 + exp(-x))

##################################################
# Logistic regression by gradient ascent         #
##################################################

# NEGATIVE Log-likelihood
def f(theta, X, y, lam):
  loglikelihood = 0
  for i in range(len(X)):
    logit = inner(X[i], theta)
    loglikelihood -= log(1 + exp(-logit))
    if not y[i]:
      loglikelihood -= logit
  for k in range(len(theta)):
    loglikelihood -= lam * theta[k]*theta[k]
  # for debugging
  # print "ll =", loglikelihood
  return -loglikelihood

# NEGATIVE Derivative of log-likelihood
def fprime(theta, X, y, lam):
  dl = [0]*len(theta)
  for i in range(len(X)):
    logit = inner(X[i], theta)
    for k in range(len(theta)):
      dl[k] += X[i][k] * (1 - sigmoid(logit))
      if not y[i]:
        dl[k] -= X[i][k]
  for k in range(len(theta)):
    dl[k] -= lam*2*theta[k]
  return numpy.array([-x for x in dl])

X_train = X[:int(len(X)/3)]
y_train = y[:int(len(y)/3)]
X_validate = X[int(len(X)/3):int(2*len(X)/3)]
y_validate = y[int(len(y)/3):int(2*len(y)/3)]
X_test = X[int(2*len(X)/3):]
y_test = y[int(2*len(X)/3):]

##################################################
# Train                                          #
##################################################

def train(lam):
  theta,_,_ = scipy.optimize.fmin_l_bfgs_b(f, [0]*len(X[0]), fprime, pgtol = 10, args = (X_train, y_train, lam))
  return theta

##################################################
# Predict                                        #
##################################################

def performance(theta):
  scores_test = [inner(theta,x) for x in X_test]
  predictions_test = [s > 0 for s in scores_test]
  correct_test = [(a==b) for (a,b) in zip(predictions_test,y_test)]

  true_positive = [(a==b) and a == True for (a,b) in zip(predictions_test,y_test)]
  true_negative = [(a==b) and a == False for (a,b) in zip(predictions_test,y_test)]
  false_positive = [(a!=b) and a == True for (a,b) in zip(predictions_test,y_test)]
  false_negative = [(a!=b) and a == False for (a,b) in zip(predictions_test,y_test)]

  #compute balanced error rate
  ber = 0.5 * (1.0 * sum(false_positive) / (sum(true_negative) + sum(false_positive)) + sum(false_negative) / (sum(true_positive) + sum(false_negative)))

  return ber, true_positive, true_negative, false_positive, false_negative

##################################################
# Precision and Recall                                        #
##################################################
def precision_and_recall(theta, top):
  scores_test = [inner(theta,x) for x in X_test]
  scores_test = sorted(scores_test, key = abs, reverse=True)

  predictions_test = [s > 0 for s in scores_test]

  precision = 1.0 * sum(predictions_test[0:top]) / top
  recall = 1.0 * sum(predictions_test[0:top]) / sum(predictions_test)

  return precision, recall

##################################################
# Validation pipeline                            #
##################################################

lam = 0.01
theta = train(lam)
ber, true_positive, true_negative, false_positive, false_negative= performance(theta)
for top in [10, 500, 1000]:
    precision, recall = precision_and_recall(theta, top)
    print("For top " + str(top) + " predictions, the precision is " + str(precision) + " ,the recall is " + str(recall))
