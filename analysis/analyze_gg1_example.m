%% Get the data
% Only read the data once to create the .mat file, as it takes very long
% time to do!
clc
clear all;

addpath('./functions')

if ~isfile('gg1_example.mat')
    path = '../simulation-results/gg1-example';
    
    if ~(check_result_path(path))
        path = '../prerun-simulation-results/gg1-example';
        check_prerun_result_path(path);
    end
    
    tests = dir(path);   
    tests(1:2) = [];
    
    m = length(tests);
    dataCell = cell(m, 2);
    
    for k = 1:m
        dataCell{k, 1} = tests(k).name;
        dat =  readtable([path '/' tests(k).name '/sim0/' 'sim-lb-allReqs.csv']);
        [f,x] = ecdf(dat.Var1);
        dataCell{k, 2} = [x,f];
    end
    
    save('gg1_example.mat', 'dataCell');
else
    tmp = load('gg1_example.mat');
    dataCell = tmp.dataCell;
    m = length(dataCell);
end


%% Compress the data and write to csv
dataPath = '../plots/data/gg1-example/';
if ~isfolder(dataPath)
    mkdir(dataPath);
end

for k=1:m
    
    name = dataCell{k, 1};
    compressed_data = compresser(dataCell{k, 2});
    filename = [dataPath name '.csv'];
    csvwrite(filename, compressed_data);
end
