from pathlib import Path
 
import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
import requests
from rasterio import features


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