from .data import (
    MissileExpressionCounts,
    Plot,
    WholeSlideImageMissileFCS,
    RegionsOfInterestPredictions,
    MissileNeighbourhoods,
    WholeSlideImage,
    DearrayedTissueMicroArrayMissileFCS,
    DearrayedTissueMicroArray,
    TissueMicroArray,
    WholeSlideImageCellSegmentationMask,
    NuclearMarkers,
    MembraneMarkers,
    MissileExpressionSpatialData,
    ProteinChannelMarkers,
    DearrayedTissueMicroArrayCellSegmentationMask,
    MissileMetadata,
    NuclearStain,
    RegionsOfInterest,
    MissileClusters,
)
from typing import List, Dict, Any, Set
from ._process import ServiceConcept, Automated, Interactive


class TechnicalVarianceCorrection(ServiceConcept):
    models: List = [
        ({TissueMicroArray}, {TissueMicroArray}),
        ({DearrayedTissueMicroArray}, {DearrayedTissueMicroArray}),
        ({WholeSlideImage}, {WholeSlideImage}),
    ]


class Start(ServiceConcept):
    models: List = [
        (
            set(),
            {
                TissueMicroArray,
                NuclearMarkers,
                NuclearStain,
                MembraneMarkers,
                ProteinChannelMarkers,
            },
        ),
        (
            set(),
            {
                WholeSlideImage,
                NuclearMarkers,
                NuclearStain,
                MembraneMarkers,
                ProteinChannelMarkers,
            },
        ),
    ]


class Plotting(ServiceConcept):
    models: List = [
        ({MissileClusters, MissileExpressionCounts, ProteinChannelMarkers}, {Plot}),
        ({MissileClusters, MissileNeighbourhoods}, {Plot}),
    ]


class FeatureExtraction(ServiceConcept):
    models: List = [
        (
            {
                NuclearMarkers,
                DearrayedTissueMicroArray,
                DearrayedTissueMicroArrayCellSegmentationMask,
                ProteinChannelMarkers,
            },
            {DearrayedTissueMicroArrayMissileFCS},
        ),
        (
            {
                WholeSlideImage,
                NuclearMarkers,
                WholeSlideImageCellSegmentationMask,
                ProteinChannelMarkers,
            },
            {WholeSlideImageMissileFCS},
        ),
    ]


class DeArray(ServiceConcept):
    models: List = [
        ({NuclearStain, TissueMicroArray}, {RegionsOfInterest}),
        ({NuclearStain, TissueMicroArray}, {RegionsOfInterestPredictions}),
        ({RegionsOfInterest, NuclearStain, TissueMicroArray}, {RegionsOfInterest}),
        (
            {NuclearStain, TissueMicroArray, RegionsOfInterestPredictions},
            {RegionsOfInterest},
        ),
        ({RegionsOfInterest, TissueMicroArray}, {DearrayedTissueMicroArray}),
    ]


class DataTransformation(ServiceConcept):
    models: List = [
        (
            {DearrayedTissueMicroArrayMissileFCS, ProteinChannelMarkers},
            {MissileExpressionCounts, MissileMetadata, MissileExpressionSpatialData},
        ),
        (
            {WholeSlideImageMissileFCS, ProteinChannelMarkers},
            {MissileExpressionCounts, MissileMetadata, MissileExpressionSpatialData},
        ),
    ]


class Clustering(ServiceConcept):
    models: List = [
        ({MissileExpressionCounts, ProteinChannelMarkers}, {MissileClusters}),
        (
            {MissileExpressionCounts, MissileMetadata, ProteinChannelMarkers},
            {MissileClusters},
        ),
        (
            {MissileClusters, MissileMetadata, MissileExpressionSpatialData},
            {MissileNeighbourhoods},
        ),
    ]


class CellSegmentation(ServiceConcept):
    models: List = [
        (
            {NuclearStain, DearrayedTissueMicroArray},
            {DearrayedTissueMicroArrayCellSegmentationMask},
        ),
        (
            {NuclearStain, MembraneMarkers, DearrayedTissueMicroArray},
            {DearrayedTissueMicroArrayCellSegmentationMask},
        ),
        ({NuclearStain, WholeSlideImage}, {WholeSlideImageCellSegmentationMask}),
        (
            {NuclearStain, MembraneMarkers, WholeSlideImage},
            {WholeSlideImageCellSegmentationMask},
        ),
    ]
