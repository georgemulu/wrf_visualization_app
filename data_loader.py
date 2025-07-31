from netCDF4 import Dataset
import xarray as xr
import requests
from wrf import destagger, getvar, interplevel
import streamlit as st
import geopandas as gpd
import numpy as np
import io
from config import STANDARD_PRESSURE_LEVELS, R2_PUBLIC_URL

@st.cache_resource
def load_wrf_data_from_r2(_=None):
    netcdf_dataset = load_netcdf_datasets(R2_PUBLIC_URL)
    xarray_dataset = load_xarray_datasets(R2_PUBLIC_URL)
    return netcdf_dataset, xarray_dataset

def load_netcdf_datasets(url):
    response = requests.get(url)
    response.raise_for_status()
    memory_file = io.BytesIO(response.content)
    return Dataset('inmemory.nc', mode='r', memory=memory_file.read())

def load_xarray_datasets(url):
    response = requests.get(url)
    response.raise_for_status()
    memory_file = io.BytesIO(response.content)
    return xr.open_dataset(memory_file)


def get_available_variables(nc):
    available = []
    if all(var in nc.variables for var in ['U10', 'V10']):
        available.append(('Wind Speed (10m)', 'surface'))
    if 'T2' in nc.variables:
        available.append(('Temperature (2m)', 'surface'))
    if 'RAINNC' in nc.variables or 'RAINC' in nc.variable:
        available.append(('Rainfall', 'surface'))   
    if 'Q2' in nc.variables or 'RH2' in nc.variables:
        available.append(('Humidity (2m)', 'surface'))    
    if all(var in nc.variables for var in ['U', 'V']):
        available.append(('Wind Speed', 'pressure'))
    if 'T' in nc.variables:
        available.append(('Temperature', 'pressure'))
    if 'rh' in nc.variables:
        available.append(('Relative Humidity', 'pressure'))

    return available, STANDARD_PRESSURE_LEVELS.copy()

def load_kenya_shapefiles(county_path, subcounty_path):
    """
    Load Kenya county and sub-county shapefiles.
    Automatically assigns EPSG:4326 if CRS is missing.
    """
    gdf = gpd.read_file(county_path)
    sub_gdf = gpd.read_file(subcounty_path)

    if gdf.crs is None:
        gdf.set_crs(epsg=4326, inplace=True)
    if sub_gdf.crs is None:
        sub_gdf.set_crs(epsg=4326, inplace=True)

    return gdf, sub_gdf

def get_rainfall(nc, time_idx):
    rain = getvar(nc, 'RAINNC', timeidx=time_idx)
    rain += getvar(nc, 'RAINC', timeidx=time_idx)
    return rain  # Total rainfall

def get_temperature(nc, time_idx, level=None):
    if level:  # pressure-level temperature
        theta = getvar(nc, "T", timeidx=time_idx)  # Potential temperature
        p = getvar(nc, "pressure", timeidx=time_idx)
        
        # Validate inputs
        if p is None or np.any(np.isnan(p)):
            raise ValueError("Invalid pressure data")
        if level < np.nanmin(p) or level > np.nanmax(p):
            raise ValueError(f"Requested level {level}hPa outside available range")
            
        # Convert potential temperature to actual temperature
        theta_interp = interplevel(theta, p, level)
        temp_k = theta_interp / ((1000.0/level)**0.286)  # Convert to Kelvin
        return temp_k - 273.15  # Convert to Celsius
    else:
        return getvar(nc, "T2", timeidx=time_idx) - 273.15
    
def get_humidity(nc, time_idx, level=None):
    if level:  # pressure-level RH
        rh = getvar(nc, "rh", timeidx=time_idx)
        p = getvar(nc, "pressure", timeidx=time_idx)
        return interplevel(rh, p, level)
    else:
        if "RH2" in nc.variables:
            return getvar(nc, "RH2", timeidx=time_idx)
        elif "Q2" in nc.variables:
            return getvar(nc, "Q2", timeidx=time_idx) * 1000  # Convert to g/kg
        else:
            return None

def get_pressure(ncfile, timeidx):
    return getvar(ncfile, "pressure", timeidx=timeidx)

def get_wind_speed(nc, time_idx, level=None):
    """
    Returns wind speed magnitude at surface (10m) or pressure level.
    """
    if level:  # pressure-level wind speed
        u = getvar(nc, "U", timeidx=time_idx)
        v = getvar(nc, "V", timeidx=time_idx)
        u = destagger(u, stagger_dim=-1)
        v = destagger(v, stagger_dim=-2)
        p = getvar(nc, "pressure", timeidx=time_idx)
        u = interplevel(u, p, level)
        v = interplevel(v, p, level)
    else:
        u= getvar(nc, "U10", timeidx=time_idx)
        v = getvar(nc, "V10", timeidx=time_idx)

    wind_speed = (u**2 + v**2)**0.5
    return wind_speed, u, v  
    
    
    
   