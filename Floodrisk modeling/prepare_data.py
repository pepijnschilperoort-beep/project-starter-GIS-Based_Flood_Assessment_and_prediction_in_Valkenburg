

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
    from owslib.wcs import WebCoverageService
    wcs = WebCoverageService('https://service.pdok.nl/rws/ahn/wcs/v1_0?SERVICE=WCS', version='1.0.0')
    response = wcs.getCoverage(identifier='dtm_05m', bbox=bbox.bounds_rd, format='GEOTIFF',
                               crs='urn:ogc:def:crs:EPSG::28992', resx=5, resy=5)

    make_path('output')
    dtm_fn = 'output/dtm.tif'
    with open(dtm_fn, 'wb') as file:
        file.write(response.read())

    return dtm_fn