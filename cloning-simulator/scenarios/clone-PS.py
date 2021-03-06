import scipy.stats
import numpy as np
from base.numerical_dist import NumericalDistribution

## Scenario used by the simulations that use one single service time distribution.
# Uses the processor sharing discipline.

nbrServers = nbrOfServers #12
seed = setSeed

for i in range(0, nbrServers):

    if dist == "fromPath":
        serviceTimeDistribution = NumericalDistribution(cdf_location=distpath, seed=seed+i*2+45567)
    elif dist != "SXmodel":
        try:
            func = getattr(scipy.stats, dist)
        except:
            raise ValueError("Distribution could not load, does it exist in scipy.stats?")
        serviceTimeDistribution = func(scale=1.0/serviceRate)
        serviceTimeDistribution.random_state = np.random.RandomState(seed=seed+i*2+45567)

    else:
        serviceTimeDistribution = None

    addServer(at=0.0, serviceTimeDistribution=serviceTimeDistribution)


changeMC(at=0.0, newMC=10000)
setRate(at = 0, rate = arrivalRateFrac*serviceRate*nbrServers)
endOfSimulation(at = 1000000/(arrivalRateFrac*nbrServers))
