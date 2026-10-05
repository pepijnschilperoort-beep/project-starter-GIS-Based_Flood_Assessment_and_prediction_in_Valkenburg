import os
from owslib.wcs import WebCoverageService
from Floodrisk_modeling.utils import BBox

def create_directories():
    """Creates the tmp and output directories within your working directory"""
    dirs = ['tmp', 'output']
    for dir in dirs:
        if not os.path.exists(dir):
            os.mkdir(dir)


def download_dtm(bbox: 'utils.BBox'):
    """Downloads elevation data for your bound inputs
        inputs: bbox
        Outputs: dtm file path (string)"""
    wcs = WebCoverageService('https://service.pdok.nl/rws/ahn/wcs/v1_0?SERVICE=WCS', version='1.0.0')
    response = wcs.getCoverage(identifier='dtm_05m', bbox=bbox.bounds_rd, format='GEOTIFF',
                               crs='urn:ogc:def:crs:EPSG::28992', resx=5, resy=5)

    make_path('output')
    dtm_fn = 'output/dtm.tif'
    with open(dtm_fn, 'wb') as file:
        file.write(response.read())

    return dtm_fn

def download_dsm(bbox: 'utils.BBox'):
    """Downloads elevation data for your bound inputs
        inputs: bbox
        Outputs: dsm file path (string)"""
    wcs = WebCoverageService('https://service.pdok.nl/rws/ahn/wcs/v1_0?SERVICE=WCS', version='1.0.0')
    response = wcs.getCoverage(identifier='dsm_05m', bbox=bbox.bounds_rd, format='GEOTIFF',
                               crs='urn:ogc:def:crs:EPSG::28992', resx=5, resy=5)

    make_path('output')
    dsm_fn = 'output/dsm.tif'
    with open(dsm_fn, 'wb') as file:
        file.write(response.read())

    return dsm_fn

def make_path(dirname, if_exists=True):
    from pathlib import Path
    Path(dirname).mkdir(exist_ok = if_exists)

def prepare_data():
    """Extracts a bounds based on user input of a city then downloads elevation data
    Outputs: DTM path(str), DSM path(str)"""
    bbox = BBox(placename = 'Valkenburg aan de Geul')
    dtm = download_dtm(bbox)
    dsm = download_dsm(bbox)
    

    return dtm, dsm