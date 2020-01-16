function [] = check_prerun_result_path(path)

    if ~isfolder(path)
       error("The simulation result path: " + path + " did not exist. \n%s", ...
             "Have you run the correct simulation or extracted the supplied pre-run simulations?")
    end

end

