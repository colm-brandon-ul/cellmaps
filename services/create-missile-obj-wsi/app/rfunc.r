MISSILe <- setClass(
  Class = 'MISSILe',
  slots = c(
    counts = 'data.frame',
    spatialdata = 'data.frame',
    metadata = 'data.frame'
    )
)

#' createMISSILeWSI - Convert WSI FCS File to Missile Object
#' @param wsidf data.frame
#' @param markerChannels character
#' 
#' @return MISSILe
createMISSILeWSI <- function(
  wsidf, 
  markerChannels #ChannelMarkers file
  ){

  # Add allRegions Column with value 1
  region <- numeric(length = dim(wsidf)[1])
  region <- as.matrix(region + 1)
  wsidf <- cbind(wsidf,region)
  colnames(wsidf)[dim(wsidf)[2]] <- "allRegions"



  # Vector of All Regions
  allRegions <- wsidf[,"allRegions"]

  # extraMetaDataColumns, # If there is extra metadata to be included from the FCS files, state numeric values of the columns that hold them.
  
  extraMetaDataColumns <- c('Size','Perimeter','MajorAxisLength','MinorAxisLength',
               'Eccentricity','Solidity','MajorMinorAxisRatio','PerimeterSquareToArea','MajorAxisToEquivalentDiam',
               'NucCytoRatio')

  # Extract Metadata Columns
  metaData <- wsidf[,extraMetaDataColumns]
  # Add AllRegions Column to Metadata
  metaData <- cbind(allRegions,metaData)

 

  # Extract Protein Count DataFrame for All Cells
  # edge case (if markerChannels is has only 1 value, returns a vector not DF (drop fixes that))
  count.data = wsidf[,markerChannels, drop = FALSE]

  # Extract Spatial Data c()
  # spatialData # Numeric values of the columns that hold the x and y coordinates
  spatialData <- c('x','y')
  spat.data = wsidf[,spatialData, drop = FALSE]

  # Create Missile Object 
  object <- new(
    Class = 'MISSILe',
    counts = count.data,
    metadata = metaData,
    spatialdata = spat.data
  )

  return(object)
}