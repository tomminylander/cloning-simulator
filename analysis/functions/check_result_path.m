function [] = check_result_path(path)

    if ~isdir(path)
       error("The simulation result path: " + path + " did not exist. \n%s", ...
             "Have you run the correct simulation or extracted the supplied pre-run simulations?")
    end

end

