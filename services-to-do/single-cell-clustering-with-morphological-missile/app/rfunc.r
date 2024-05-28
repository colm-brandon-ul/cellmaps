library(FastPG)

#' clusterMISSILe
#' @param ExpressionObject Expression
#' @param MetaDataObject data.frame
#' @param markers character
#' @param metadata character
#' @param numNeighbours numeric, default: 0
#' 
#' @return SingleCellClusters
clusterMISSILeWithMetadata <- function(
    ExpressionCounts, 
    MetaData,
    markers, 
    numNeighbours = 20){
    
    # will come back to excluding metadata
    Rphenograph_out <- FastPG::fastCluster(
        data = as.matrix(cbind(ExpressionCounts[,markers],MetaData[,colnames((MetaData))])), 
        k = numNeighbours, 
        num_threads = 1,
        verbose = TRUE)         
    


    return(data.frame(cluster_labels = as.numeric(Rphenograph_out[[2]])))
}