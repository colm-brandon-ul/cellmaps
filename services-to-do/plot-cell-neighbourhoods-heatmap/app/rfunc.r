# Data input
  # SingleCellClusters
    # cluster_labels
  # NeighbourhoodClusters
    # cluster_labels

# Service Params;
  # colorLimits - -4 to +4
  # colorPal - any three combinations of colours

library(ComplexHeatmap)
library(png)

neighbourhoodEnrichment <- function (SingleCellClusters,NeighbourhoodClusters, colorLimits = c(-1.5, 0, 1.5), colorPal = c("#027BD0","white","#E94558")){

  phenotypes <- droplevels(as.factor(SingleCellClusters$cluster_labels))

  neighbourhoodAbundance <- matrix(NA, nrow = length(levels(phenotypes)), ncol = length(unique(NeighbourhoodClusters$cluster_labels)))
  rownames(neighbourhoodAbundance) <- levels(phenotypes)
  
  neighbourhooodSize <- numeric(length(unique(NeighbourhoodClusters$cluster_labels)))
  
  for (j in 1:ncol(neighbourhoodAbundance)) {
    
    phenotypesNeigh <- phenotypes[NeighbourhoodClusters$cluster_labels ==  j]
    
    b <- table(phenotypesNeigh)
    
    for (i in 1:nrow(neighbourhoodAbundance)) {
      neighbourhoodAbundance[i, j] <- as.numeric(b[i])/length(phenotypesNeigh)
    }
    
    print(paste0("Neighbourhood ", j, " = ", 
                 length(phenotypesNeigh)))
    
    neighbourhooodSize[j] <- length(phenotypesNeigh)
  }
  
  neighbourhoodAbundanceNorm <- neighbourhoodAbundance
  
  for (i in 1:nrow(neighbourhoodAbundance)) {
    neighbourhoodAbundanceNorm[i, ] <- (neighbourhoodAbundance[i, ] - min(neighbourhoodAbundance[i, ]))/(max(neighbourhoodAbundance[i,]) - min(neighbourhoodAbundance[i, ]))
  }
  
  colnames(neighbourhoodAbundanceNorm) <- paste0("Neighbourhood - ", c(1:ncol(neighbourhoodAbundanceNorm)))
  
  a <- t(apply(neighbourhoodAbundance, MARGIN = 1, scale))
  
  colnames(a) <- paste0("N-", c(1:ncol(neighbourhoodAbundanceNorm)))
  
  row_ha = ComplexHeatmap::rowAnnotation(Size = ComplexHeatmap::anno_barplot(neighbourhooodSize, bar_width = 0.5, gp = grid::gpar(fill = "black")))
  
  hm = ComplexHeatmap::Heatmap(as.matrix(t(a)), col = circlize::colorRamp2(c(colorLimits[1], 
                                                                        colorLimits[2], colorLimits[3]), c(colorPal[1], colorPal[2], colorPal[3])), 
                          border = FALSE, rect_gp = grid::gpar(col = "grey80", 
                                                               lwd = 1), name = "Enrichment", right_annotation = row_ha, 
                          row_names_gp = grid::gpar(fontsize = 11), column_names_gp = grid::gpar(fontsize = 11), 
                          column_title = "", column_title_gp = grid::gpar(fontsize = 13, 
                                                                          fontface = "bold"), clustering_distance_rows = "euclidean", 
                          clustering_distance_columns = "euclidean", cluster_rows = FALSE, 
                          heatmap_legend_param = list(title = "Enrichment", 
                                                      title_gp = grid::gpar(fontsize = 9, fontface = "bold"), 
                                                      legend_height = unit(4, "cm"), title_position = "leftcenter-rot"))


  # Write plot Disk -> Generic Function for all items which return plots
  png("temp-file.png")
  draw(hm)
  dev.off()

  # ggsave('temp-file.png',plot)
  # Read plot file from disk as Array
  y <- readPNG("temp-file.png")
  # Delete file from Disk
  file.remove("temp-file.png")
  
  print(typeof(y))
  # Return Array
  return (y)

    
}