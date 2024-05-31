
# import libraries
library(RANN)
library(plyr)

cellNeighbourhoods <- function(
    metadata, SingleCellClusters, 
    spatial_data, numOfCells = 10, kMeans = 10){

    # internal functions
    nearestNeighbourPhenotypes.internal <- function(NN, phenotypes = phenotypes){
    toReplace <- phenotypes[NN]
    return(toReplace)
    }


    countCellPhenotypes.internal <- function(counts, phenotypes = phenotypes, levels = NULL){
    phenoCounts <- plyr::count(counts)
    cellNeighNeigh <- t(as.data.frame(numeric(length(levels))))
    cellNeighNeigh[phenoCounts$x] <- phenoCounts$freq
    return(cellNeighNeigh)
    }
 

    # Get unique set of regions
    
    phenotypeLevels <- unique(SingleCellClusters$cluster_labels)

    regionIDs <- unique(metadata$allRegions)

  
    #
    for(k in 1:length(regionIDs)){



      ## get co-ordinates
      coordinates <- spatial_data[metadata$allRegions == regionIDs[k],]

      ## get phenotypes within that region
      phenotypes <- as.numeric(SingleCellClusters$cluster_labels[metadata$allRegions == regionIDs[k]]) - 1

      cellNeighbourhoodsTemp <- matrix(NA, nrow = length(phenotypes), ncol = numOfCells)

        # apply nearest neighbour to spatial data in region (spatial cluster of cells)
      nn <- RANN::nn2(coordinates, k = numOfCells)
    
            # including phenotypes to spatial clustering
      cellNeighbourhoodsTemp <- t(
        apply(nn$nn.idx, 
        MARGIN = 1,
        FUN = nearestNeighbourPhenotypes.internal, 
        phenotypes))


        # counting phenotypes in spatial cluster
      cellNeigh <- suppressWarnings(t(apply(cellNeighbourhoodsTemp,
       MARGIN = 1, 
       FUN = countCellPhenotypes.internal, 
       phenotypes, levels = phenotypeLevels)))

      if(k == 1){
        # creating initial dataframe
        cellNeighbourhoodsData <- cellNeigh
      } else {
        # appeneding to dataframe
        cellNeighbourhoodsData <- rbind(cellNeighbourhoodsData, cellNeigh)
      }

    }

    # kmeans clustering
    clusters <- kmeans(cellNeighbourhoodsData, centers = kMeans)$cluster

    # return dataframe of labels
  return(data.frame(cluster_labels = clusters))

}