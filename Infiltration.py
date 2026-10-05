
from pathlib import Path
import matplotlib.pyplot as plt
import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
import requests
from rasterio import features
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

bbox = BBox(placename = 'Valkenburg aan de Geul')




BOFEK_URL = "https://bodemdata.nl/files/download/BOFEK_2020_Shape.zip"
BOFEK_FILE =  "data/bofek2020.zip"


def download(url, dest):
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)

    if dest.exists():
        print(f"Already exists: {dest}")
        return dest

    print(f"Downloading:\n{url}")

    part = dest.with_suffix(dest.suffix + ".part")

    with requests.get(url, stream=True, timeout=120) as r:
        r.raise_for_status()

        with open(part, "wb") as f:
            for chunk in r.iter_content(1024 * 1024):
                if chunk:
                    f.write(chunk)

    part.rename(dest)

    print(f"Saved: {dest}")
    return dest



download(BOFEK_URL,BOFEK_FILE)

bofek = gpd.read_file("data/BOFEK2020.gpkg"
)

print("BOFEK CRS:", bofek.crs)
print("BOFEK columns:")
print(bofek.columns.tolist())




SOIL_URL = (
    "https://data.source.coop/cholmes/portolan-nl/vro/bodemkaart/"
    "soilarea/soilarea.parquet"
)
DTM_PATH = "data/dtm.tif"                 # your AHN GeoTIFF (EPSG:28992)
SOIL_CACHE = Path("data/soilarea.parquet")
OUT_PATH = "data/infiltration_mm_h.tif"

def download(url, dest):
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        return dest
    part = dest.with_suffix(dest.suffix + ".part")
    with requests.get(url, stream=True, timeout=60) as r:
        r.raise_for_status()
        with open(part, "wb") as f:
            for chunk in r.iter_content(1 << 20):
                f.write(chunk)
    part.rename(dest)
    return dest

a=download(SOIL_URL,'data/soilarea.parquet')
soil = gpd.read_parquet("data/soilarea.parquet")

print(soil.head())
print(soil.columns)
print(soil.crs)
