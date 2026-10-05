import osmnx as ox
import pyproj
from shapely.geometry import box
from shapely.ops import transform

class BBox:
    def __init__(self, placename=None, bounds_rd=None, epsg_code='28992'):
        self.epsg_code = epsg_code
        if placename:
            self.init_from_placename(placename)
        elif bounds_rd:
            self.bounds_rd = bounds_rd
            self.geom_rd = box(*bounds_rd)
            self.set_4326()
        else:
            raise ValueError("Either placename or bounds_rd must be provided.")

    def init_from_placename(self, placename):
        place_gdf = ox.geocoder.geocode_to_gdf(placename)
        if len(place_gdf) == 1:
            place_gdf = place_gdf.to_crs(f'EPSG:{self.epsg_code}')
            self.bounds_rd = [float(val) for val in place_gdf.total_bounds]
            self.geom_rd = box(*self.bounds_rd)
            self.set_4326()
        else:
            raise ValueError("Placename not found in OpenStreetMap.")

    def set_4326(self):
        project = pyproj.Transformer.from_crs(self.epsg_code, '4326', always_xy=True).transform
        self.geom_4326 = transform(project, self.geom_rd)
        self.bounds_4326 = list(self.geom_4326.bounds)

    def set_28992(self):
        project = pyproj.Transformer.from_crs(self.epsg_code, '28992', always_xy=True).transform
        self.geom_28992 = transform(project, self.geom_rd)
        self.bounds_28992 = list(self.geom_28992.bounds)