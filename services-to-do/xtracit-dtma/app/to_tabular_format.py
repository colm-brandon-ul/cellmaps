import numpy as np
import pandas as pd
from skimage.measure import regionprops_table

COLUMN_NAMES = ['Cell_ID','Region','x','y','Size','Perimeter','MajorAxisLength','MinorAxisLength',
                   'Eccentricity','Solidity','MajorMinorAxisRatio','PerimeterSquareToArea','MajorAxisToEquivalentDiam',
                   'NucCytoRatio']
    
REGION_PROPERTIES = ['area','centroid', 'perimeter',  
                      'major_axis_length','minor_axis_length', 'eccentricity', 'solidity', 
                      'orientation','equivalent_diameter','coords','label']

# regionprops_table For Mapping from REGION_PROPERTIES to  COLUMN_NAMES
COL_REGION_MAP = {
    'x' : 'centroid-1',
    'y' : 'centroid-0',
    'Size' : 'area',
    'Perimeter' : 'perimeter',
    'MajorAxisLength' : 'major_axis_length',
    'MinorAxisLength' : 'minor_axis_length',
    'Eccentricity' : 'eccentricity',
    'Solidity' : 'solidity'
}

NUC_COLUMN_NAMES = ['Cell_ID','nucleus_Region','nucleus_x','nucleus_y','nucleus_Size']
NUCLEUS_PROPERTIES = ['area','centroid','label','coords']

NUC_COL_REGION_MAP = {
    'nucleus_x' : 'centroid-1',
    'nucleus_y' : 'centroid-0',
    'nucleus_Size' : 'area',
}

# Function for leverage pandas vectorization
# For each row, it iterates of the list of coordinates, gets the means intensity for all the protein channels 
def get_protein_signal_for_cells(coords, area, channel_stack):
    all_signal_counts_for_cell = []
    for coord in coords:
        col, row = coord
        all_signal_counts_for_cell.append(channel_stack[col, row,:])
        
    return np.sum(all_signal_counts_for_cell,axis=0) / area

def extract_membrane_for_core(membrane_mask,channel_stack,core_name,channels_to_include):
    # Using the mask, find the coordinates of all the cells, and the locations of the pixels within those cells
    extractedDataMemTab = pd.DataFrame(regionprops_table(membrane_mask.astype(int), properties=REGION_PROPERTIES))
    
    # The is creating the template of the final dataframe
    df = pd.DataFrame(index=np.arange(extractedDataMemTab.shape[0]), columns=COLUMN_NAMES)
    # In the final dataframe, copy over the cell ids (adjust to start from 1) + copy in the core name number (again starting counting from 1) 
    df['Cell_ID'] = extractedDataMemTab.index + 1
    df['Region'] = int(core_name.replace('A','')) + 1
    
    # Copy Morphological data from region prop data to final dataframe
    for k,v in COL_REGION_MAP.items():
        df[k] = extractedDataMemTab[v]
    
    # Create some new morphological features
    df['MajorMinorAxisRatio'] = df['MajorAxisLength'] / df['MinorAxisLength']
    df['PerimeterSquareToArea'] = np.square(df['Perimeter']) / df['Size']
    df['MajorAxisToEquivalentDiam'] = df['MajorAxisLength'] / extractedDataMemTab['equivalent_diameter']
    
    # Create a dataframe for the storing the outcoming of the extraction of the signals
    cell_signal_df = pd.DataFrame()
    # Extracts the signal intensities for all cells and stores it in a dataframe
    cell_signal_df[channels_to_include] = extractedDataMemTab.apply(lambda x: get_protein_signal_for_cells(x.coords, x.area,channel_stack), axis=1).apply(pd.Series)
    
    return pd.concat([df,cell_signal_df],axis=1,join='inner')

def extract_nucelus_for_core(nucleus_mask,channel_stack,core_name,channels_to_include):
    # Using the mask, find the coordinates of all the cells, and the locations of the pixels within those cells
    extractedDataNucTab = pd.DataFrame(regionprops_table(nucleus_mask.astype(int), properties=NUCLEUS_PROPERTIES))
    
    # The is creating the template of the final dataframe
    df = pd.DataFrame(index=np.arange(extractedDataNucTab.shape[0]), columns=NUC_COLUMN_NAMES)
    # In the final dataframe, copy over the cell ids (adjust to start from 1) + copy in the core name number (again starting counting from 1) 
    df['Cell_ID'] = extractedDataNucTab.index + 1
    df['nucleus_Region'] = int(core_name.replace('A','')) + 1
    
    # Copy Morphological data from region prop data to final dataframe
    for k,v in NUC_COL_REGION_MAP.items():
        df[k] = extractedDataNucTab[v]
    
   
    
    # Create a dataframe for the storing the outcoming of the extraction of the signals
    cell_signal_df = pd.DataFrame()
    # Extracts the signal intensities for all cells and stores it in a dataframe
    cell_signal_df[channels_to_include] = extractedDataNucTab.apply(lambda x: get_protein_signal_for_cells(x.coords, x.area,channel_stack), axis=1).apply(pd.Series)
    
    return pd.concat([df,cell_signal_df],axis=1,join='inner')
    

def get_final_dataframe(a: pd.DataFrame,b: pd.DataFrame) :
    # Merge the two columns based on cell id, this will drop any nuclei / membranes that do not have a corresponidng nuclei / membrane
    c = pd.merge(a,b, on='Cell_ID')
    c['NucCytoRatio'] = c.nucleus_Size / c.Size
    return c.drop(columns=['nucleus_Region','nucleus_x','nucleus_y','nucleus_Size'])


