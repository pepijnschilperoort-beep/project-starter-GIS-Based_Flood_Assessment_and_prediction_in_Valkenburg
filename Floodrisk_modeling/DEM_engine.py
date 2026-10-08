import rasterio
import numpy as np
import richdem as rd
from pysheds.grid import Grid
from prepare_data import download_dtm

def condition_dem(dem_path="tmp/DEM.tif"):
    """
    Fills artificial sinks and depressions using RichDEM so water 
    can route continuously across the DEM.
    """
    # 1. Read the array AND the spatial metadata
    with rasterio.open(dem_path) as file:
        dem = file.read(1, masked=True).filled(np.nan).astype(np.float32)
        meta = file.meta.copy()  # Save metadata for exporting later
    
    # 2. 
    rd_dem = rd.rdarray(dem, no_data=np.nan)
    
    # 3. Fill depressions (in_place modifies rd_dem directly)
    rd.FillDepressions(rd_dem, epsilon=True, in_place=True)
    
    # # 4. Convert back to a standard NumPy array
    # filled_dem = np.array(rd_dem)
    
    # 5. Export the filled DEM safely using the original metadata
    output_path = "tmp/filled_dem.tif"
    meta.update(dtype=rasterio.float32, nodata=np.nan)
    
    with rasterio.open(output_path, 'w', **meta) as dst:
        dst.write(rd_dem, 1)
    
    
    return rd_dem

# np.in1d is not supported so change it with np.isin
if not hasattr(np, 'in1d'):
    np.in1d = np.isin
    
def route_flow(dem_path="tmp/filled_dem.tif"):
    """
    Uses PySheds to calculate D8 Flow Direction and Flow Accumulation.
    """
    # np.in1d is not supported so change it with np.isin
    if not hasattr(np, 'in1d'):
        np.in1d = np.isin
        
    # 1. Instantiate the grid directly from the TIFF
    grid = Grid.from_raster(dem_path)
    
    # 2. Read the raster data into a PySheds Raster object
    dem = grid.read_raster(dem_path)
    
    # 3. Calculate Flow Direction (D8 routing) - REMOVED 'data='
    flowdir = grid.flowdir(dem = dem, routing='d8', dirmap = (64, 128, 1, 2, 4, 8, 16, 32))
    
    # 4. Calculate Flow Accumulation - REMOVED 'data='
    flow_acc = grid.accumulation(fdir = flowdir, dirmap=(64, 128, 1, 2, 4, 8, 16, 32), routing = 'd8', nodata_out=0.0)

    # 5. Export directly using PySheds' built-in rasterio wrapper
    output_path = "tmp/accumulation.tif"
    grid.to_raster(flow_acc, output_path)

    # 5. Export directly using PySheds' built-in rasterio wrapper
    output_path = "tmp/flowdir.tif"
    grid.to_raster(flowdir, output_path)
    
    return flowdir
