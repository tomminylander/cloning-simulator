function exists = check_result_path(path)
    exists = 1;
    if ~isfolder(path)
       warning("The simulation result path: " + path + " did not exist. \n%s", ...
             "Checking pre-run simulation result path instead...")
       exists = 0;
    end

end