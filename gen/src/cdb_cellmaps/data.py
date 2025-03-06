from typing import List, Dict, Any, Set
import sys
from ._data import (
    PNG,
    TorchScript,
    StringMixin,
    HashMapMixin,
    NonAtomic,
    OMETIFF,
    ListMixin,
    CSV,
    Atomic,
)
from typing_extensions import override


class RegionOfInterest(Atomic):
    """This class describes a region of interest."""

    x1: float
    y1: float
    x2: float
    y2: float
    img_w: float
    img_h: float

    def __init__(
        self, x1: float, y1: float, x2: float, y2: float, img_w: float, img_h: float
    ) -> None:
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.img_w = img_w
        self.img_h = img_h

    @classmethod
    def decode(cls, data) -> "RegionOfInterest":
        instance = cls(
            x1=data["x1"],
            y1=data["y1"],
            x2=data["x2"],
            y2=data["y2"],
            img_w=data["img_w"],
            img_h=data["img_h"],
        )
        return instance

    def encode(self) -> dict:
        return self.__dict__


class ProteinChannelMarker(str, StringMixin, Atomic):
    """This class describes a protein channel marker."""

    def __init__(self, value) -> None: ...

    def __new__(cls, value):
        return super().__new__(cls, value)

    @classmethod
    def decode(cls, data) -> "ProteinChannelMarker":
        return cls(data)

    @override
    def encode(self) -> str:
        return str(self)


class NuclearStain(str, StringMixin, Atomic):
    """This class describes a nuclear stain."""

    def __init__(self, value) -> None: ...

    def __new__(cls, value):
        return super().__new__(cls, value)

    @classmethod
    def decode(cls, data) -> "NuclearStain":
        return cls(data)

    @override
    def encode(self) -> str:
        return str(self)


class NuclearMarker(str, StringMixin, Atomic):
    """This class describes a nuclear marker."""

    def __init__(self, value) -> None: ...

    def __new__(cls, value):
        return super().__new__(cls, value)

    @classmethod
    def decode(cls, data) -> "NuclearMarker":
        return cls(data)

    @override
    def encode(self) -> str:
        return str(self)


class MembraneMarker(str, StringMixin, Atomic):
    """This class describes a membrane marker."""

    def __init__(self, value) -> None: ...

    def __new__(cls, value):
        return super().__new__(cls, value)

    @classmethod
    def decode(cls, data) -> "MembraneMarker":
        return cls(data)

    @override
    def encode(self) -> str:
        return str(self)


class RegionsOfInterest(ListMixin[RegionOfInterest], NonAtomic):
    """This class describes a list of regions of interest."""

    data: List[RegionOfInterest]

    def __init__(self) -> None:
        self.data = []

    @classmethod
    def decode(cls, data) -> "RegionsOfInterest":
        instance = cls()
        for v in data:
            instance.data.append(RegionOfInterest.decode(v))
        return instance

    def encode(self) -> list:
        return [v.encode() for v in self.data]


class TissueCoreNucleusSegmentationMask(OMETIFF, Atomic):
    """This class describes a nucleus segmentation mask in a Tissue Core."""

    url: str

    def __init__(self, url) -> None:
        super().__init__(url)

    @classmethod
    def decode(cls, data) -> "TissueCoreNucleusSegmentationMask":
        instance = cls(url=data["url"])
        return instance

    def encode(self) -> dict:
        return self.__dict__


class TissueCoreMembraneSegmentationMask(OMETIFF, Atomic):
    """This class describes a membrane segmentation mask in a Tissue Core."""

    url: str

    def __init__(self, url) -> None:
        super().__init__(url)

    @classmethod
    def decode(cls, data) -> "TissueCoreMembraneSegmentationMask":
        instance = cls(url=data["url"])
        return instance

    def encode(self) -> dict:
        return self.__dict__


class TissueCoreProteinChannel(OMETIFF, Atomic):
    """This class describes a protein channel in a Tissue Core."""

    url: str

    def __init__(self, url) -> None:
        super().__init__(url)

    @classmethod
    def decode(cls, data) -> "TissueCoreProteinChannel":
        instance = cls(url=data["url"])
        return instance

    def encode(self) -> dict:
        return self.__dict__


class WholeSlideImageMissileFCS(CSV, Atomic):
    """This class describes a missile FCS in a Whole Slide Image."""

    _SCHEMA = {
        "*": float,
        "x": int,
        "y": int,
        "Size": int,
        "Perimeter": float,
        "MajorAxisLength": float,
        "MinorAxisLength": float,
        "Eccentricity": float,
        "Solidity": float,
        "MajorMinorAxisRatio": float,
        "PerimeterSquareToArea": float,
        "MajorAxisToEquivalentDiam": float,
        "NucCytoRatio": float,
        "Cell_ID": int,
        "Region": int,
    }
    url: str

    def __init__(self, url) -> None:
        super().__init__(url)

    @classmethod
    def decode(cls, data) -> "WholeSlideImageMissileFCS":
        instance = cls(url=data["url"])
        return instance

    def encode(self) -> dict:
        return {k: v for k, v in self.__dict__.items() if k[0] != "_"}


class TissueCoreMissileFCS(CSV, Atomic):
    """This class describes a missile FCS in a Tissue Core."""

    _SCHEMA = {
        "*": float,
        "x": int,
        "y": int,
        "Size": int,
        "Perimeter": float,
        "MajorAxisLength": float,
        "MinorAxisLength": float,
        "Eccentricity": float,
        "Solidity": float,
        "MajorMinorAxisRatio": float,
        "PerimeterSquareToArea": float,
        "MajorAxisToEquivalentDiam": float,
        "NucCytoRatio": float,
        "Cell_ID": int,
        "Region": int,
    }
    url: str

    def __init__(self, url) -> None:
        super().__init__(url)

    @classmethod
    def decode(cls, data) -> "TissueCoreMissileFCS":
        instance = cls(url=data["url"])
        return instance

    def encode(self) -> dict:
        return {k: v for k, v in self.__dict__.items() if k[0] != "_"}


class MissileNeighbourhoods(CSV, Atomic):
    """This class describes missile neighbourhoods."""

    _SCHEMA = {
        "cluster_labels": int,
    }
    url: str

    def __init__(self, url) -> None:
        super().__init__(url)

    @classmethod
    def decode(cls, data) -> "MissileNeighbourhoods":
        instance = cls(url=data["url"])
        return instance

    def encode(self) -> dict:
        return {k: v for k, v in self.__dict__.items() if k[0] != "_"}


class MissileMetadata(CSV, Atomic):
    """This class describes missile metadata."""

    _SCHEMA = {
        "allRegions": int,
        "Size": int,
        "Perimeter": float,
        "MajorAxisLength": float,
        "MinorAxisLength": float,
        "Eccentricity": float,
        "Solidity": float,
        "MajorMinorAxisRatio": float,
        "PerimeterSquareToArea": float,
        "MajorAxisToEquivalentDiam": float,
        "NucCytoRatio": float,
    }
    url: str

    def __init__(self, url) -> None:
        super().__init__(url)

    @classmethod
    def decode(cls, data) -> "MissileMetadata":
        instance = cls(url=data["url"])
        return instance

    def encode(self) -> dict:
        return {k: v for k, v in self.__dict__.items() if k[0] != "_"}


class MissileExpressionSpatialData(CSV, Atomic):
    """This class describes missile expression spatial data."""

    _SCHEMA = {
        "x": int,
        "y": int,
    }
    url: str

    def __init__(self, url) -> None:
        super().__init__(url)

    @classmethod
    def decode(cls, data) -> "MissileExpressionSpatialData":
        instance = cls(url=data["url"])
        return instance

    def encode(self) -> dict:
        return {k: v for k, v in self.__dict__.items() if k[0] != "_"}


class MissileExpressionCounts(CSV, Atomic):
    """This class describes missile expression counts."""

    _SCHEMA = {
        "*": float,
    }
    url: str

    def __init__(self, url) -> None:
        super().__init__(url)

    @classmethod
    def decode(cls, data) -> "MissileExpressionCounts":
        instance = cls(url=data["url"])
        return instance

    def encode(self) -> dict:
        return {k: v for k, v in self.__dict__.items() if k[0] != "_"}


class MissileClusters(CSV, Atomic):
    """This class describes missile clusters."""

    _SCHEMA = {
        "cluster_labels": int,
    }
    url: str

    def __init__(self, url) -> None:
        super().__init__(url)

    @classmethod
    def decode(cls, data) -> "MissileClusters":
        instance = cls(url=data["url"])
        return instance

    def encode(self) -> dict:
        return {k: v for k, v in self.__dict__.items() if k[0] != "_"}


class Plot(PNG, Atomic):
    """This class describes a plot. Could make this less generic (i.e. to plot type)"""

    url: str

    def __init__(self, url) -> None:
        super().__init__(url)

    @classmethod
    def decode(cls, data) -> "Plot":
        instance = cls(url=data["url"])
        return instance

    def encode(self) -> dict:
        return self.__dict__


class WholeSlideImageProteinChannel(OMETIFF, Atomic):
    """This class describes a protein channel in a Whole Slide Image."""

    url: str

    def __init__(self, url) -> None:
        super().__init__(url)

    @classmethod
    def decode(cls, data) -> "WholeSlideImageProteinChannel":
        instance = cls(url=data["url"])
        return instance

    def encode(self) -> dict:
        return self.__dict__


class WholeSlideImageNucleusSegmentationMask(OMETIFF, Atomic):
    """This class describes a nucleus segmentation mask in a Whole Slide Image."""

    url: str

    def __init__(self, url) -> None:
        super().__init__(url)

    @classmethod
    def decode(cls, data) -> "WholeSlideImageNucleusSegmentationMask":
        instance = cls(url=data["url"])
        return instance

    def encode(self) -> dict:
        return self.__dict__


class WholeSlideImageMembraneSegmentationMask(OMETIFF, Atomic):
    """This class describes a membrane segmentation mask in a Whole Slide Image."""

    url: str

    def __init__(self, url) -> None:
        super().__init__(url)

    @classmethod
    def decode(cls, data) -> "WholeSlideImageMembraneSegmentationMask":
        instance = cls(url=data["url"])
        return instance

    def encode(self) -> dict:
        return self.__dict__


class TissueMicroArrayProteinChannel(OMETIFF, Atomic):
    """This class describes a protein channel in a Tissue MicroArray."""

    url: str

    def __init__(self, url) -> None:
        super().__init__(url)

    @classmethod
    def decode(cls, data) -> "TissueMicroArrayProteinChannel":
        instance = cls(url=data["url"])
        return instance

    def encode(self) -> dict:
        return self.__dict__


class DeArrayModelPt(TorchScript, Atomic):
    """This class describes a dearraying model using the torchscript model format"""

    url: str

    def __init__(self, url) -> None:
        super().__init__(url)

    @classmethod
    def decode(cls, data) -> "DeArrayModelPt":
        instance = cls(url=data["url"])
        return instance

    def encode(self) -> dict:
        return self.__dict__


class RegionsOfInterestPredicition(NonAtomic):
    """This class describes a prediction of regions of interest."""

    confidence_value: float
    rois: RegionsOfInterest

    def __init__(self, confidence_value: float, rois: RegionsOfInterest) -> None:
        self.confidence_value = confidence_value
        self.rois = rois

    @classmethod
    def decode(cls, data) -> "RegionsOfInterestPredicition":
        instance = cls(
            confidence_value=data["confidence_value"],
            rois=RegionsOfInterest.decode(data["rois"]),
        )
        return instance

    def encode(self) -> dict:
        return {
            "confidence_value": self.confidence_value,
            "rois": self.rois.encode(),
        }


class TissueCoreCellSegmentationMask(NonAtomic):
    """This class describes a cell segmentation mask in a Tissue Core. Which contains
    a nucleus mask"""

    membrane_mask: TissueCoreMembraneSegmentationMask
    nucleus_mask: TissueCoreNucleusSegmentationMask

    def __init__(
        self,
        membrane_mask: TissueCoreMembraneSegmentationMask,
        nucleus_mask: TissueCoreNucleusSegmentationMask,
    ) -> None:
        self.membrane_mask = membrane_mask
        self.nucleus_mask = nucleus_mask

    @classmethod
    def decode(cls, data) -> "TissueCoreCellSegmentationMask":
        instance = cls(
            membrane_mask=TissueCoreMembraneSegmentationMask.decode(
                data["membrane_mask"]
            ),
            nucleus_mask=TissueCoreNucleusSegmentationMask.decode(data["nucleus_mask"]),
        )
        return instance

    def encode(self) -> dict:
        return {
            "membrane_mask": self.membrane_mask.encode(),
            "nucleus_mask": self.nucleus_mask.encode(),
        }


class TissueCore(HashMapMixin[str, TissueCoreProteinChannel], NonAtomic):
    """This class describes a Tissue Core."""

    data: Dict[str, TissueCoreProteinChannel]

    def __init__(self) -> None:
        self.data = {}

    @classmethod
    def decode(cls, data) -> "TissueCore":
        instance = cls()
        for k, v in data.items():
            instance.data[k] = TissueCoreProteinChannel.decode(v)
        return instance

    def encode(self) -> dict:
        return {k: v.encode() for k, v in self.data.items()}


class RegionsOfInterestPredictions(ListMixin[RegionsOfInterestPredicition], NonAtomic):
    """This class describes a list of regions of interest predictions."""

    data: List[RegionsOfInterestPredicition]

    def __init__(self) -> None:
        self.data = []

    @classmethod
    def decode(cls, data) -> "RegionsOfInterestPredictions":
        instance = cls()
        for v in data:
            instance.data.append(RegionsOfInterestPredicition.decode(v))
        return instance

    def encode(self) -> list:
        return [v.encode() for v in self.data]


class ProteinChannelMarkers(ListMixin[ProteinChannelMarker], NonAtomic):
    """This class describes a list of protein channel markers."""

    data: List[ProteinChannelMarker]

    def __init__(self) -> None:
        self.data = []

    @classmethod
    def decode(cls, data) -> "ProteinChannelMarkers":
        instance = cls()
        for v in data:
            instance.data.append(ProteinChannelMarker.decode(v))
        return instance

    def encode(self) -> list:
        return [v.encode() for v in self.data]


class NuclearMarkers(ListMixin[NuclearMarker], NonAtomic):
    """This class describes a list of nuclear markers."""

    data: List[NuclearMarker]

    def __init__(self) -> None:
        self.data = []

    @classmethod
    def decode(cls, data) -> "NuclearMarkers":
        instance = cls()
        for v in data:
            instance.data.append(NuclearMarker.decode(v))
        return instance

    def encode(self) -> list:
        return [v.encode() for v in self.data]


class MembraneMarkers(ListMixin[MembraneMarker], NonAtomic):
    """This class describes a list of membrane markers."""

    data: List[MembraneMarker]

    def __init__(self) -> None:
        self.data = []

    @classmethod
    def decode(cls, data) -> "MembraneMarkers":
        instance = cls()
        for v in data:
            instance.data.append(MembraneMarker.decode(v))
        return instance

    def encode(self) -> list:
        return [v.encode() for v in self.data]


class WholeSlideImage(HashMapMixin[str, WholeSlideImageProteinChannel], NonAtomic):
    """This class describes a Whole Slide Image."""

    data: Dict[str, WholeSlideImageProteinChannel]

    def __init__(self) -> None:
        self.data = {}

    @classmethod
    def decode(cls, data) -> "WholeSlideImage":
        instance = cls()
        for k, v in data.items():
            instance.data[k] = WholeSlideImageProteinChannel.decode(v)
        return instance

    def encode(self) -> dict:
        return {k: v.encode() for k, v in self.data.items()}


class TissueMicroArray(HashMapMixin[str, TissueMicroArrayProteinChannel], NonAtomic):
    """This class describes a Tissue MicroArray."""

    data: Dict[str, TissueMicroArrayProteinChannel]

    def __init__(self) -> None:
        self.data = {}

    @classmethod
    def decode(cls, data) -> "TissueMicroArray":
        instance = cls()
        for k, v in data.items():
            instance.data[k] = TissueMicroArrayProteinChannel.decode(v)
        return instance

    def encode(self) -> dict:
        return {k: v.encode() for k, v in self.data.items()}


class DearrayedTissueMicroArrayMissileFCS(
    HashMapMixin[str, TissueCoreMissileFCS], NonAtomic
):
    """This class describes a Dearrayed Tissue MicroArray Missile FCS."""

    data: Dict[str, TissueCoreMissileFCS]

    def __init__(self) -> None:
        self.data = {}

    @classmethod
    def decode(cls, data) -> "DearrayedTissueMicroArrayMissileFCS":
        instance = cls()
        for k, v in data.items():
            instance.data[k] = TissueCoreMissileFCS.decode(v)
        return instance

    def encode(self) -> dict:
        return {k: v.encode() for k, v in self.data.items()}


class DearrayedTissueMicroArrayCellSegmentationMask(
    HashMapMixin[str, TissueCoreCellSegmentationMask], NonAtomic
):
    """This class describes a Dearrayed Tissue MicroArray Cell Segmentation Mask(s)."""

    data: Dict[str, TissueCoreCellSegmentationMask]

    def __init__(self) -> None:
        self.data = {}

    @classmethod
    def decode(cls, data) -> "DearrayedTissueMicroArrayCellSegmentationMask":
        instance = cls()
        for k, v in data.items():
            instance.data[k] = TissueCoreCellSegmentationMask.decode(v)
        return instance

    def encode(self) -> dict:
        return {k: v.encode() for k, v in self.data.items()}


class DearrayedTissueMicroArray(HashMapMixin[str, TissueCore], NonAtomic):
    """This class describes a Dearrayed Tissue MicroArray."""

    data: Dict[str, TissueCore]

    def __init__(self) -> None:
        self.data = {}

    @classmethod
    def decode(cls, data) -> "DearrayedTissueMicroArray":
        instance = cls()
        for k, v in data.items():
            instance.data[k] = TissueCore.decode(v)
        return instance

    def encode(self) -> dict:
        return {k: v.encode() for k, v in self.data.items()}


class WholeSlideImageCellSegmentationMask(NonAtomic):
    """This class describes a cell segmentation mask in a Whole Slide Image. Which
    contains a nucleus and membrane mask"""

    membrane_mask: WholeSlideImageMembraneSegmentationMask
    nucleus_mask: WholeSlideImageNucleusSegmentationMask

    def __init__(
        self,
        membrane_mask: WholeSlideImageMembraneSegmentationMask,
        nucleus_mask: WholeSlideImageNucleusSegmentationMask,
    ) -> None:
        self.membrane_mask = membrane_mask
        self.nucleus_mask = nucleus_mask

    @classmethod
    def decode(cls, data) -> "WholeSlideImageCellSegmentationMask":
        instance = cls(
            membrane_mask=WholeSlideImageMembraneSegmentationMask.decode(
                data["membrane_mask"]
            ),
            nucleus_mask=WholeSlideImageNucleusSegmentationMask.decode(
                data["nucleus_mask"]
            ),
        )
        return instance

    def encode(self) -> dict:
        return {
            "membrane_mask": self.membrane_mask.encode(),
            "nucleus_mask": self.nucleus_mask.encode(),
        }
