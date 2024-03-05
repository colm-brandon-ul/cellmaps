library(FastPG)

#' clusterMISSILe
#' @param ExpressionObject Expression
#' @param markers character
#' @param numNeighbours numeric, default: 0
#' 
#' @return SingleCellClusters
clusterMISSILe <- function(
    ExpressionCounts, 
    markers, 
    numNeighbours = 20){
 
    Rphenograph_out <- FastPG::fastCluster(
        data = as.matrix(ExpressionCounts[,markers]), 
        k = numNeighbours, 
        num_threads = 1,
        verbose = TRUE)         
    
    
    # Return single column DF with name cluster_labels
    return(data.frame(cluster_labels = as.integer(Rphenograph_out[[2]])))
}