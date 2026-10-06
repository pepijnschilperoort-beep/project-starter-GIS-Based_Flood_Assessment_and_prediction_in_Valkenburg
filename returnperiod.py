## In this file you will find two functions
## The first function will return the daily rainfall based 
## The second function will return the extreme intense rainfall per hour



#package use
import pandas as pd
import requests
import zipfile
import matplotlib.pyplot as plt
from scipy.stats import genextreme 
import numpy as np
from io import BytesIO, StringIO

# check the return peirod input conditions
# it will stop working when input is smaller than or equal to one 
def calculate_rainfall(return_period):
  if not np.isfinite(return_period) or return_period <= 1:
    raise ValueError("Return period must be greater than 1 year.")

#download the wearther data from knmi
  url = "https://cdn.knmi.nl/knmi/map/page/klimatologie/gegevens/daggegevens/etmgeg_380.zip"

  response = requests.get(url)
  response.raise_for_status()

#upzip the file and read the TXT file
  with zipfile.ZipFile(BytesIO(response.content)) as z:
    text = z.read("etmgeg_380.txt").decode("utf-8-sig")

# Find the header containing the column names, and skip the introduction message in file
# all the head are messy, so use "," to splits it up
  for i, line in enumerate(text.splitlines()):
    if line.strip().startswith("# STN"):
        columns = line.replace("#", "").strip().split(",")
        columns = [col.strip() for col in columns]
        header_row = i
        break

# Read the data into a DataFrame
  df = pd.read_csv(
        StringIO(text),
        skiprows=header_row + 1,
        names=columns,
        skipinitialspace=True,
        na_values=["", " "],
        low_memory=False
    )

# Conver dates
  df["date"] = pd.to_datetime(
        df["YYYYMMDD"].astype(str),
        format="%Y%m%d"
    )
# Select 1975–2025
  df = df[
        (df["date"] >= "1975-01-01")
        & (df["date"] <= "2025-12-31")
    ].copy()

# RH to numeric values + turn units to mm+ -1 in datasets means 0.05mm<
  df["RH"] = pd.to_numeric(df["RH"], errors="coerce")
  df["rainfall_mm"] = df["RH"].replace(-1, 0) / 10
# Calculate the maximum daily rainfall for each year
  annual_max = df.groupby(
        df["date"].dt.year
    )["rainfall_mm"].max().dropna()

# fits the GEV distribution(Generalized Extreme Value distribution)
  shape, loc, scale = genextreme.fit(annual_max)

# Convert the return period to a probability
  probability = 1 - 1 / return_period

# Estimate the corresponding daily rainfall
  rainfall = genextreme.ppf(probability,shape,loc=loc,scale=scale)

  return float(rainfall)


### This function takes a return period in years as input and estimates 
### the corresponding daily rainfall amount in millimetres for the flood model.
rainfall_mm = calculate_rainfall(30)
print(" daily rainfall:", rainfall_mm, "mm")

#----------------------------------------------------------------------------------#
## This is the function for hourly extreme rainfall

def calculate_hourly_extreme(return_period):
  if not np.isfinite(return_period) or return_period <= 1:
    raise ValueError("Return period must be greater than 1 year.")

# download the wearther data from knmi
  url = "https://cdn.knmi.nl/knmi/map/page/klimatologie/gegevens/daggegevens/etmgeg_380.zip"

  response = requests.get(url)
  response.raise_for_status()

#upzip the file and read the TXT file
  with zipfile.ZipFile(BytesIO(response.content)) as z:
    text = z.read("etmgeg_380.txt").decode("utf-8-sig")

# Find the header containing the column names, and skip the introduction message in file
# all the head are messy, so use "," to splits it up
  for i, line in enumerate(text.splitlines()):
    if line.strip().startswith("# STN"):
        columns = line.replace("#", "").strip().split(",")
        columns = [col.strip() for col in columns]
        header_row = i
        break

# Read the data into a DataFrame
  df = pd.read_csv(
        StringIO(text),
        skiprows=header_row + 1,
        names=columns,
        skipinitialspace=True,
        na_values=["", " "],
        low_memory=False
    )

# Conver dates
  df["date"] = pd.to_datetime(
        df["YYYYMMDD"].astype(str),
        format="%Y%m%d"
    )
# Select 1975–2025
  df = df[
        (df["date"] >= "1975-01-01")
        & (df["date"] <= "2025-12-31")
    ].copy()

# RHX to numeric values + turn units to mm+ -1 in datasets means 0.05mm<
  df["RHX"] = pd.to_numeric(df["RHX"], errors="coerce")
  df["rainfall_mm"] = df["RHX"].replace(-1, 0) / 10
# Calculate the maximum daily rainfall for each year
  annual_max = df.groupby(
        df["date"].dt.year
    )["rainfall_mm"].max().dropna()

# fits the GEV distribution(Generalized Extreme Value distribution)
  shape, loc, scale = genextreme.fit(annual_max)

# Convert the return period to a probability
  probability = 1 - 1 / return_period

# Estimate the corresponding daily rainfall
  rainfall = genextreme.ppf(probability,shape,loc=loc,scale=scale)

  return float(rainfall)

#Here you can type in the 
#Input : "different return period"
#Output: "intensity of extremely rainfall with the units of mm/hour "
intensity_mm_h = calculate_hourly_extreme(50)
print("extreme one-hour intensity:", intensity_mm_h, "mm/h")