import rasterio
import numpy as np
import richdem as rd

def prepare_data():
    """Extracts a bounds based on user input of a city then downloads elevation data
    Outputs: DTM path(str), DSM path(str)"""
    from MCDA.utils import BBox
    create_directories()
    bbox = BBox(placename = 'Valkenburg')
    dtm = download_dtm(bbox)
    

    return dtm, networkbuffer

#combine DTM and DSM to create a new DEM

#def prepare_data():
    return


#def 