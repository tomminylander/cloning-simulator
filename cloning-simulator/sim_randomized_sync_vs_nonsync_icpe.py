import os
import sys
import numpy as np
from multiprocessing import Pool
import random as xxx_random # prevent accidental usage
from base.utils import *

## Script that runs the randomized sync vs non-sync simulations for the ICPE-2020 paper

if len(sys.argv) == 4:
    scen_min = int(sys.argv[1])
    scen_max = int(sys.argv[2])
    seed_input = int(sys.argv[3])
else:
    print("No input, setting to default")
    scen_min = 0
    scen_max = 1000
    seed_input = 222454


rnd = xxx_random.Random()
rnd.seed(seed_input)

# Parameters
NBR_SCENARIOS = range(scen_min, scen_max)

dists = ["SXmodel", "expon", "pareto", "uniform", "weibull_min"]
utils = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
nbrServers = [4, 6, 9, 12, 15, 21, 27, 30, 45, 48]

PROCESSES = 24
MAXRUNTIME = 10000

def getRandomCloneFactor(nbrServers):
    cloneFactors = []
    for nbr in range(2, nbrServers):
        if nbrServers % nbr == 0:
            cloneFactors.append(nbr)

    return rnd.choice(cloneFactors)

# Add simulation commands as strings
simulations = []

count = 0
for scenario in NBR_SCENARIOS:

    dist = rnd.choice(dists)
    util = rnd.choice(utils)
    nbrServer = rnd.choice(nbrServers)
    cloneFactor = getRandomCloneFactor(nbrServer)
    frac = getLambdaFrac(dist, util, cloneFactor)

    resultPath = "../simulation-results/randomized-sync-vs-nonsync/scenario{}".format(scenario)
    if not os.path.isdir(resultPath):
        os.makedirs(resultPath)

    count += 1
    simulations.append("./simulator.py  --lb cluster-SQF --scenario scenarios/clone-PS-randomized.py --cloning 1 --nbrClones {} \
        --printout 0 --printRespTime 0 --dist {} --serviceRate 1.0 --arrivalRateFrac {} --nbrOfServers {} \
        --setSeed {} --maxRunTime {} --outdir {}/clusterSQF-PS \
        ".format(cloneFactor, dist, frac, nbrServer, count*100 + 123456, MAXRUNTIME, resultPath))

    count += 1
    simulations.append("./simulator.py  --lb cluster-random --scenario scenarios/clone-PS-randomized.py --cloning 1 --nbrClones {} \
        --printout 0 --printRespTime 0 --dist {} --serviceRate 1.0 --arrivalRateFrac {} --nbrOfServers {} \
        --setSeed {} --maxRunTime {} --outdir {}/clusterRandom-PS \
        ".format(cloneFactor, dist, frac, nbrServer, count*100 + 123456, MAXRUNTIME, resultPath))

    count += 1
    simulations.append("./simulator.py  --lb clone-SQF --scenario scenarios/clone-PS-randomized.py --cloning 1 --nbrClones {} \
        --printout 0 --printRespTime 0 --dist {} --serviceRate 1.0 --arrivalRateFrac {} --nbrOfServers {} \
        --setSeed {} --maxRunTime {} --outdir {}/SQF-PS \
        ".format(cloneFactor, dist, frac, nbrServer, count*100 + 123456, MAXRUNTIME, resultPath))

    count += 1
    simulations.append("./simulator.py  --lb clone-random --scenario scenarios/clone-PS-randomized.py --cloning 1 --nbrClones {} \
        --printout 0 --printRespTime 0 --dist {} --serviceRate 1.0 --arrivalRateFrac {} --nbrOfServers {} \
        --setSeed {} --maxRunTime {} --outdir {}/Random-PS \
        ".format(cloneFactor, dist, frac, nbrServer, count*100 + 123456, MAXRUNTIME, resultPath))

    with open("{}/description.csv".format(resultPath), 'a') as f:
        f.write("dist,{}\nutil,{}\nnbrServer,{}\ncloneFactor,{}\nlambdafrac,{}".format(dist, util, nbrServer, cloneFactor, frac))


# Run the simulations
pool = Pool(processes=PROCESSES)
for k, simulation in enumerate(simulations):
    simulation += " --printsim {}".format(k+1)
    pool.apply_async(os.system, (simulation,))

pool.close()
pool.join()
print "All simulations completed"
