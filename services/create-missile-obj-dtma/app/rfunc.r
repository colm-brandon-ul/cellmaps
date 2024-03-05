MISSILe <- setClass(
  Class = 'MISSILe',
  slots = c(
    counts = 'data.frame',
    spatialdata = 'data.frame',
    metadata = 'data.frame'
    )
)

#' createMISSILeTMA - Convert TMA FCS Files to Missile Object
#' @param data.lists list[data.frame]
#' @param markerChannels character
#' 
#' @return MISSILe
createMISSILeTMA <- function(
  data.lists, 
  markerChannels #ChannelMarkers file
  ){

  # Iterate Over the dataframes
  for(k in 1:length(data.lists)){
    region <- numeric(length = dim(data.lists[[k]])[1])
    region <- as.matrix(region + k)
    # add new region column to DF
    data.lists[[k]] <- cbind(data.lists[[k]],region)
    # Rename the region column and 
    colnames(data.lists[[k]])[dim(data.lists[[k]])[2]] <- "allRegions"
  }

   # combine the dataframes into a single DF
  flatList <- do.call(rbind.data.frame, data.lists)

  # Vector of All Regions
  allRegions <- flatList[,"allRegions"]

  # extraMetaDataColumns, # If there is extra metadata to be included from the FCS files, state numeric values of the columns that hold them.
  
  extraMetaDataColumns <- c('Size','Perimeter','MajorAxisLength','MinorAxisLength',
               'Eccentricity','Solidity','MajorMinorAxisRatio','PerimeterSquareToArea','MajorAxisToEquivalentDiam',
               'NucCytoRatio')

  # Extract Metadata Columns
  metadata <- flatList[,extraMetaDataColumns, drop = FALSE]
  # Add AllRegions Column to Metadata
  metadata <- cbind(allRegions,metadata)



  # Extract Protein Count DataFrame for All Cells
  

  countdata = flatList[,markerChannels, drop = FALSE]

  # Extract Spatial Data c()
  # spatialData # Numeric values of the columns that hold the x and y coordinates
  spatialData <- c('x','y')
  spat.data = flatList[,spatialData, drop = FALSE]

  
  # Create Missile Object 
  object <- new(
    Class = 'MISSILe',
    counts = countdata,
    spatialdata = spat.data,
    metadata = metadata
  )

  return(object)
}