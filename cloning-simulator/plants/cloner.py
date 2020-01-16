from __future__ import division
import csv
import math
import numpy as np
import random as xxx_random # prevent accidental usage
from base import Request
from base.utils import *


## Simulates a request cloner.
class Cloner:

    ## Constructor
    # @param setSeed The random seed
    def __init__(self, setSeed=123):
        self.seed = setSeed

        self.cloning = 0
        self.nbrClones = 1

        self.random = xxx_random.Random()
        self.random.seed(self.seed)

        self.activeRequests = {}

        self.dolly = np.asarray(self.readCsv('dists/dolly.csv'))

        self.processorShareVarCoeff = 0.0
        self.processorShareMean = 0.0

        self.reqNbr = 0

        self.sim = None

    ## Set a reference to the simulator kernel sim
    def setSim(self, sim):
        self.sim = sim

    ## Set if cloning should be active
    def setCloning(self, cloning):
        self.cloning = cloning

    ## Set number of clones to use (1 if no cloning)
    def setNbrClones(self, nbrClones):
        self.nbrClones = nbrClones

    ## Creates a clone of the specified request and stores it
    # @param request The request to clone
    def clone(self, request):
        if not self.cloning:
            return None

        shouldClone = self.shouldClone(request)

        if not shouldClone:
            key = request.requestId
            if key not in self.activeRequests:
                self.activeRequests[request.requestId] = [request]
            return None

        clone = self.createClone(request)
        otherClones = self.getClones(request)

        self.setIllegalServers(request, clone, otherClones)

        return clone

    ## Checks if the request has been cancelled
    # @param request The request to check
    def isCanceled(self, request):
        if not self.cloning:
            return False

        key = request.requestId
        if key in self.activeRequests:
            return False
        else:
            return True

    ## Cancels all clones associated with the specified request
    # @param request The request of interest
    def cancelAllClones(self, request):
        if not self.cloning:
            return

        clones = self.getClones(request)
        if not clones:
            return

        processorShares = []

        for i in range(0, len(clones)):
            clone = clones[i]
            if not hasattr(clone, 'isCompleted') and hasattr(clone, 'chosenBackend'):
                if hasattr(clone, 'lastCheckpoint'):
                    clone.chosenBackend.updateAvgProcessorShare(clone)

                clone.isCanceled = True
                clone.chosenBackend.onCanceled(clone)

            if hasattr(clone, 'avgProcessorShare'):
                processorShares.append(clone.avgProcessorShare)

        # Collect some statistics on processor shares for the clones
        self.processorShareMean = (self.processorShareMean*self.reqNbr + avg(processorShares))/(self.reqNbr+1)
        self.processorShareVarCoeff = (self.processorShareVarCoeff*self.reqNbr + np.std(processorShares)/avg(processorShares))/(self.reqNbr+1)

        self.reqNbr += 1

        self.deleteClones(request)

    ## Sets service times for all clones related to a specific request
    # @param request The request of interest
    def setCloneServiceTimes(self, request):
        if not self.cloning:
            return

        clones = self.getClones(request)

        if not clones:
            return

        taskSize = self.drawHyperExpServiceTime()
        for i in range(0, len(clones)):
            if not hasattr(clones[i], 'serviceTime'):
                slowdownFactor = clones[i].chosenBackend.dollySlowdown
                slowdown = self.drawDollySlowdown(slowdownFactor)
                serviceTime = slowdown*taskSize
                self.activeRequests[request.requestId][i].serviceTime = serviceTime

    ## Checks if the specified request should be cloned
    # @param request The request of interest
    def shouldClone(self, request):
        currentNbrClones = self.getNbrClones(request)
        diff = self.nbrClones - currentNbrClones
        if diff >= 1.0:
            return True
        elif (diff < 1.0) and (diff > 0.0):
            return self.random.uniform(0, 1) <= diff
        else:
            return False

    ## Creates a clone of the specified request
    # @param request The request of interest
    def createClone(self, request):
        clone = Request()
        clone.createdAt = request.createdAt
        clone.requestId = request.requestId
        clone.originalRequest = request.originalRequest
        clone.isClone = True
        clone.illegalServers = []

        return clone

    ## Gets the number of clones associated to the specific request
    # @param request The request of interest
    def getNbrClones(self, request):
        currentClones = self.getClones(request)
        nbrClones = 1
        if currentClones:
            nbrClones = len(currentClones)

        return nbrClones

    ## Set what servers the clone should not be sent to (i.e.
    #  servers where clones of the same request have been sent)
    # @param request The request to clone
    # @param clone The clone of the request
    # @param otherClones Already existing clones of the same request
    def setIllegalServers(self, request, clone, otherClones):
        if otherClones:
            for i in range(0, len(otherClones)):
                clone.illegalServers.append(otherClones[i].chosenBackendIndex)
            self.activeRequests[request.requestId].append(clone)
        else:
            self.activeRequests[request.requestId] = [request, clone]
            clone.illegalServers.append(request.chosenBackendIndex)

    ## Gets clones associated with the specific request
    # @param request The request of interest
    def getClones(self, request):
        if not self.cloning:
            return None

        key = request.requestId
        if key in self.activeRequests:
            clones = self.activeRequests[key]
            return clones
        else:
            return None

    ## Deletes all clones associated to the specific request
    # @param request The request of interest
    def deleteClones(self, request):
        del self.activeRequests[request.requestId]

    ## Draws a hyper-exponential service time
    # @param p The probability to choose the first exponential distribution (denoted by mu1)
    # @param mu1 The service rate of the first exponential distribution
    # @param mu2 The service rate of the second exponential distribution
    def drawHyperExpServiceTime(self, p=None, mu1=None, mu2=None):

        if p is None:
            coeff = 2.0
            hypermean = 1.0/4.7
            p1 = 0.5 * (1.0 + math.sqrt((coeff - 1.0) / (coeff + 1.0)))
            p2 = 1.0 - p1
            mu1 = 2.0 * p1 / hypermean
            mu2 = 2.0 * p2 / hypermean

            if self.random.uniform(0, 1) <= p1:
                return self.random.expovariate(mu1)
            else:
                return self.random.expovariate(mu2)
        else:
            if self.random.uniform(0, 1) <= p:
                return self.random.expovariate(mu1)
            else:
                return self.random.expovariate(mu2)

    ## Draws s server slowdown represented by the Dolly distribution with a specific slowdown factor
    # @param slowdownFactor The slowdown factor use
    def drawDollySlowdown(self, slowdownFactor):
        slowint = self.random.randint(0, 999)
        slowdown = self.dolly.item(slowint)
        return slowdown*slowdownFactor

    ## Reads a csv file that contains the cdf of the distribution
    # @param filename The name of the file that contains the cdf (in csv format)
    def readCsv(self, filename):
        floatvector = []
        with open(filename, 'r') as f:
            reader = csv.reader(f)
            for v in reader:
                floatvector.append(float(v[0]))
        return floatvector

