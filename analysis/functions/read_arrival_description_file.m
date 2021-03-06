function data = read_arrival_description_file(filepath)

tmp = readtable(filepath);

dist_tmp = tmp.Properties.VariableNames(2);
dist = dist_tmp{1};

values = tmp.(2);
util = values(1);
nbrServer = values(2);
cloneFactor = values(3);
meanServiceTime = values(4);
lambdaFrac = values(5);
arrivalDelay = values(6);

data.dist = dist;
data.util = util;
data.nbrServer = nbrServer;
data.cloneFactor = cloneFactor;
data.meanServiceTime = meanServiceTime;
data.lambdaFrac = lambdaFrac;
data.arrivalDelay = arrivalDelay;
end