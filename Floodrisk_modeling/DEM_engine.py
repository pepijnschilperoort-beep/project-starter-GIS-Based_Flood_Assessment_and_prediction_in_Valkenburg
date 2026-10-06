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


# def route_flow(dem_path = "tmp/filled_dem.tif" ):
#         """
#         Uses PySheds to calculate D8 Flow Direction and Flow Accumulation.
#         """
        
#         # 1. Instantiate the PySheds grid using your spatial metadata
#         with rasterio.open(dem_path) as file:
#             dem = file.read(1, masked=True).filled(np.nan).astype(np.float32)
#             meta = file.meta.copy()
#             transform = file.transform
#             crs = file.crs
        
#         grid = Grid(dem) 
        
#         # 2. Load our customized, memory-resident array into the grid
#         # We use grid.add_gridded_data to bypass loading from disk again
#         grid.add_gridded_data(dem, data_name='dem', affine=transform, crs=crs)
        
#         # 3. Calculate Flow Direction (D8 routing)
#         flow_dir = grid.flowdir(data='dem', dirmap=(64, 128, 1, 2, 4, 8, 16, 32))
        
#         # 4. Calculate Flow Accumulation
#         flow_acc = grid.accumulation(data=flow_dir, dirmap=(64, 128, 1, 2, 4, 8, 16, 32))

#         output_path = "tmp/accumulation.tif"
#         meta.update(dtype=rasterio.float32, nodata=np.nan)
    
#         with rasterio.open(output_path, 'w', **meta) as dst:
#             dst.write(flow_acc, 1)
        
#         return flow_acc

def route_flow(dem_path="tmp/filled_dem.tif"):
    """
    Uses PySheds to calculate D8 Flow Direction and Flow Accumulation.
    """
    
    # 1. Instantiate the grid directly from the TIFF (handles transform/CRS automatically)
    grid = Grid.from_raster(dem_path)
    
    # 2. Read the raster data into a PySheds Raster object
    dem = grid.read_raster(dem_path)
    
    # 3. Calculate Flow Direction (D8 routing)
    flow_dir = grid.flowdir(data=dem, dirmap=(64, 128, 1, 2, 4, 8, 16, 32))
    
    # 4. Calculate Flow Accumulation
    flow_acc = grid.accumulation(data=flow_dir, dirmap=(64, 128, 1, 2, 4, 8, 16, 32))

    # 5. Export directly using PySheds' built-in rasterio wrapper
    output_path = "tmp/accumulation.tif"
    grid.to_raster(flow_acc, output_path)
    
    print(f"Flow accumulation saved to: {output_path}")
    return flow_acc
