library(ggplot2)
library(png)

# Interactive Service -> Select Cluster to Ignore?
# Renaming Plots ->

#' BubblePlotMissile
#' @param ExpressionObject Expression
#' @param SingleCellClustersObject SingleCellClusters
#' @param markers character
#' @param ignoreClusters character
#' @param threshold.percent numeric, default: 0
#' @param colour.scale numeric, default: c(0,3)
#' @param colours character, default: c("#132B43","#FF0000")
#' @param transposePlot logical, default: FALSE
#' 
#' @return double
BubblePlotMissile <- function(
  ExpressioCounts,
  Clusters,
  markers,
  transposePlot = FALSE,
  threshold.percent = 0, # This is tool parameter
  colour.scale = c(0,3),
  colours = c("#132B43","#FF0000"),
  ignoreClusters = NULL
) {

  # Get's set of cluster_labels
  uniqueClusters <- levels(as.factor(Clusters$cluster_labels))

  # Filters clusters to be ingored from uniquecluster
  if(!is.null(ignoreClusters)){
    uniqueClusters <- uniqueClusters[! uniqueClusters %in% ignoreClusters]
  }

  # Create empty dataframe
  plottingDF <- data.frame(matrix(nrow = length(markers) * length(uniqueClusters), ncol = 4))
  # Name columns
  colnames(plottingDF) <- c("Cluster","Protein","Percent.Exp","Mean.Exp")

  # Populate Protein Columns
  plottingDF$Protein <- rep(markers, times = length(uniqueClusters))

  # Populate Clusters Columns
  plottingDF$Cluster <- rep(uniqueClusters, each = length(markers))

  # Filter out the protein counts and cluster labels to be used in plotting
  if(!is.null(ignoreClusters)){
    dataToScale <- Clusters[!(Clusters$cluster_labels %in% ignoreClusters),markers]
    labelsOfInterest <- Clusters$cluster_labels[!(Clusters$cluster_labels %in% ignoreClusters)]

  } else {
    dataToScale <- Clusters[,markers]
    labelsOfInterest <- Clusters$cluster_labels
  }

  # Scaling data by column
  scaledData <- as.data.frame(apply(dataToScale, MARGIN = 2, scale))

  # Loop over all Clusters
  for(i in 1:length(uniqueClusters)){
    # Filter out clusters at current index
    tempClusterData <- scaledData[labelsOfInterest == uniqueClusters[i],]

    # Create two empty vectors for..
    meanExpression <- numeric(length(markers))
    aboveThreshold <- numeric(length(markers))

    # loop over all markers
    for(j in 1:length(markers)){
      # Populate vectors for cluster marker index i
      meanExpression[j] <- mean(tempClusterData[,markers[j]])
      aboveThresholdTemp <- tempClusterData[,markers[j]] > threshold.percent
      aboveThreshold[j] <- (length(aboveThresholdTemp[aboveThresholdTemp == TRUE]) / length(aboveThresholdTemp))*100
    }

    # Add to plotting DF
    plottingDF$Percent.Exp[plottingDF$Cluster == uniqueClusters[i]] <- aboveThreshold
    plottingDF$Mean.Exp[plottingDF$Cluster == uniqueClusters[i]] <- meanExpression
  }

  # Setting limits for color scale for plot
  plottingDF$Mean.Exp[plottingDF$Mean.Exp > colour.scale[2]] <- colour.scale[2]
  plottingDF$Mean.Exp[plottingDF$Mean.Exp < colour.scale[1]] <- colour.scale[1]

  # Setting limits for the Bubble Size
  plottingDF$Percent.Exp[plottingDF$Percent.Exp > 100] <- 100
  plottingDF$Percent.Exp[plottingDF$Percent.Exp < 50] <- 50


 # Plotting with GGPLOT
  plot <- ggplot(
    data = plottingDF, 
    mapping = aes_string(x = 'Protein', y = 'Cluster')) +
    geom_point(mapping = aes_string(size = 'Percent.Exp', color = 'Mean.Exp')) +
    guides(size = guide_legend(title = 'Percent Expressed')) + 
    theme_bw() +
    xlab("") + 
    ylab("") +
    theme(axis.text.x = element_text(angle = 45, hjust = 1, size = 12),
          axis.text.y = element_text(size = 12),
          panel.grid.major = element_blank(),
          panel.grid.minor = element_blank()) + 
    scale_colour_gradient2(
      low = colours[1],
      high = colours[2],
      space = "Lab",
      na.value = "grey50",
      guide = "colourbar",
      aesthetics = "colour") +
    scale_y_discrete(breaks = unique(plottingDF$Cluster))


    if(transposePlot == TRUE){
      plot + coord_flip()
    }

    # Write plot Disk -> Generic Function for all items which return plots
    ggsave('temp-file.png',plot)
    # Read plot file from disk as Array
    y <- readPNG("temp-file.png")
    # Delete file from Disk
    file.remove('temp-file.png')
    
    print(typeof(y))
    # Return Array
    return (y)
}