# This seems to work and throws an error when the package isn't installed!
# install remotes if not installed
if (!requireNamespace("remotes", quietly = TRUE))
    withCallingHandlers(install.packages("remotes"), warning = function(w) stop(w))

# Get the file name from command line argument
args <- commandArgs(trailingOnly = TRUE)
file_name <- args[1]

# Open the file
file <- file(file_name, "r")

# Iterate over the lines of the file
while (length(line <- suppressWarnings(readLines(file, n = 1))) > 0) {
    # Split the columns
    columns <- strsplit(line, ",")[[1]]
    package <- columns[1]
    installer <- columns[2]
    repos <- columns[3]
    # Process each line here
    
     # must be regular package
    if (is.na(installer) | installer == "" | installer == "NA") {
        if (!requireNamespace("package", quietly = TRUE)){

            if (is.na(repos) | repos == "" | repos == "NA"){
                print("installing from CRAN")
                withCallingHandlers(install.packages(package, repos="https://cloud.r-project.org"), warning = function(w) stop(w))
            }
            else{
                withCallingHandlers(install.packages(package, repos = repos), warning = function(w) stop(w))
            }
        }
        
    }
    
    else if(installer == "BiocManager"){
        # make sure BiocManager is installed
        if (!requireNamespace("BiocManager", quietly = TRUE))
            if (!requireNamespace("package", quietly = TRUE)){
            withCallingHandlers(install.packages("BiocManager", repos="https://cloud.r-project.org"), warning = function(w) stop(w))
            }
            # install package
            library(BiocManager)
            withCallingHandlers(BiocManager::install(package), warning = function(w) stop(w))

    }
    
    # must be devtools
    else if (installer == "devtools"){
        if (!requireNamespace("devtools", quietly = TRUE))
            withCallingHandlers(install.packages("devtools"), warning = function(w) stop(w))
        library(devtools)
        if (is.na(repos) | repos == "" | repos == "NA"){
            withCallingHandlers(devtools::install_github(package), warning = function(w) stop(w))
        }
        else{
            withCallingHandlers(devtools::install_github(package, repos = repos), warning = function(w) stop(w))
        }
    }
    # must be remotes
    else if (installer == "remotes"){
        if (!requireNamespace("remotes", quietly = TRUE))
            withCallingHandlers(install.packages("remotes"), warning = function(w) stop(w))
        library(remotes)
        if (is.na(repos) | repos == "" | repos == "NA"){
            withCallingHandlers(remotes::install_github(package), warning = function(w) stop(w))
        }
        else{
            withCallingHandlers(remotes::install_github(package, repos = repos), warning = function(w) stop(w))
        }
    }

   

    else{
        stop("ERROR: installer not recognized")
    }

}

# Close the file
close(file)
