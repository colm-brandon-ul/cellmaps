import os
from . import data
from . import process

# Need to figure out how to populate these things automatically
__version__ = "0.0.1a1000208"
__detailed_version__ = "0.0.1+ds.0.0.1.0.2.8" #type: ignore
__library_name__ = 'cdb_cellmaps' #type: ignore

__export__ = ["data", "process", "__version__", "__detailed_version__", "__library_name__"]