
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
from rasterio.transform import from_origin
from rasterio.features import rasterize
import rasterio
import rasterio.plot
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

bofek = gpd.read_file("data/bofek2020/BOFEK_2020.shp"
)

print("BOFEK CRS:", bofek.crs)
print("BOFEK columns:")
print(bofek.columns.tolist())


bofek = bofek.to_crs("EPSG:28992")

# Create a GeoDataFrame containing the bbox
bbox_gdf = gpd.GeoDataFrame(
    {"geometry": [bbox.geom_rd]},
    crs="EPSG:28992"
)

# Clip BOFEK polygons to the bbox
bofek_clipped = gpd.clip(bofek, bbox_gdf)

print("Original BOFEK polygons:", len(bofek))
print("Clipped BOFEK polygons:", len(bofek_clipped))

# Save the clipped shapefile
bofek_clipped.to_file(
    "data/bofek2020/bofek2020_valkenburg.shp"
)

# Plot to check
fig, ax = plt.subplots(figsize=(10, 10))
bofek_clipped.plot(ax=ax, column='BOFEK2020', categorical=True,
    legend=True,
    edgecolor="black",
    linewidth=0.5)
bbox_gdf.boundary.plot(ax=ax, color="red", linewidth=2)

plt.show()
bofek_valkenburg=bofek_clipped

ksat_table = pd.DataFrame({
    "BOFEK2020": [
        4013,
        4016,
        4018,
        4019,
        4020,
        5002,
        5004,
        5007],
    "Ksat": [
        1.74,
        3.0,
        3.0,
        6.31,
        3.77,
        0.99,
        29.83,
        6.31
    ]
})

bofek_ksat = bofek_valkenburg.merge(
    ksat_table,
    on="BOFEK2020",
    how="left"
)
bofek_ksat["Ksat"] = bofek_ksat["Ksat"].fillna(6)

minx, miny, maxx, maxy = bbox.geom_rd.bounds
resolution = 5
transform = from_origin(
    minx,
    maxy,
    resolution,
    resolution
)
width = int(np.ceil((maxx - minx) / resolution))
height = int(np.ceil((maxy - miny) / resolution))
shapes = (
    (geom, ksat)
    for geom, ksat in zip(
        bofek_ksat.geometry,
        bofek_ksat["Ksat"]
    )
)
ksat_raster = rasterize(
    shapes=shapes,
    out_shape=(height, width),
    transform=transform,
    fill=6,                 
    dtype="float32"
)

output_file = "data/ksat_valkenburg_0.5m.tif"

with rasterio.open(
    output_file,
    "w",
    driver="GTiff",
    height=height,
    width=width,
    count=1,
    dtype="float32",
    crs="EPSG:28992",
    transform=transform
) as dst:
    dst.write(ksat_raster, 1)

print(f"Saved: {output_file}")

fig, ax = plt.subplots(figsize=(10, 10))

rasterio.plot.show(
    ksat_raster,
    transform=transform,
    ax=ax,
    cmap="viridis"
)

ax.set_title("Ksat raster – 1 × 1 m")
ax.set_xlabel("RD X (m)")
ax.set_ylabel("RD Y (m)")

plt.tight_layout()
plt.show()

cell_area = 5 * 5
dt_hours = 1.0
n_timesteps = 48

ksat_mm_h=ksat_raster/24*10
surface_water = np.zeros_like(ksat_raster, dtype=np.float32)  # m/hour
F_mm = np.zeros_like(ksat_raster, dtype=np.float32)
f0_mm_h = 5
F_decay_mm = 20.0
rainfall_mm_h = np.zeros(n_timesteps)
rainfall_mm_h[:] = 5.0

surface_water_history = np.zeros(
    (n_timesteps + 1, *ksat_raster.shape),
    dtype=np.float32
)

F_history = np.zeros(
    (n_timesteps + 1, *ksat_raster.shape),
    dtype=np.float32
)

surface_water_history[0] = surface_water
F_history[0] = F_mm


for t in range(n_timesteps):

    # ----------------------------------------------
    # 1. Add rainfall
    # ----------------------------------------------

    rainfall_depth_m = rainfall_mm_h[t] / 1000.0

    rainfall_volume = rainfall_depth_m * cell_area

    surface_water += rainfall_volume

    # ----------------------------------------------
    # 2. Calculate infiltration capacity
    #
    # f(F) = Ksat + (f0 - Ksat) * exp(-F/F_decay)
    # ----------------------------------------------

    infiltration_capacity_mm_h = (
        ksat_mm_h
        + (f0_mm_h - ksat_mm_h)
        * np.exp(-F_mm / F_decay_mm)
    )

    potential_infiltration_mm = (
        infiltration_capacity_mm_h * dt_hours
    )

    potential_infiltration_m = (
        potential_infiltration_mm / 1000.0
    )

    potential_infiltration_volume = (
        potential_infiltration_m * cell_area
    )

    infiltration_volume = np.minimum(
        surface_water,
        potential_infiltration_volume
    )

    surface_water -= infiltration_volume
        
    infiltration_depth_mm = (
        infiltration_volume / cell_area * 1000.0
    )

    F_mm += infiltration_depth_mm

    surface_water_history[t + 1] = surface_water
    F_history[t + 1] = F_mm