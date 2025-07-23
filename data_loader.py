from netCDF4 import Dataset
from wrf import getvar, interplevel
import streamlit as st
import geopandas as gpd
import numpy as np
import io
from config import STANDARD_PRESSURE_LEVELS, LOAD_FROM_DRIVE
from drive_auth import authenticate_drive

@st.cache_resource
def load_wrf_data(file_path_or_id):
    if LOAD_FROM_DRIVE:
        return load_netcdf_from_drive(file_path_or_id)
    else:
        return Dataset(file_path_or_id)

def load_netcdf_from_drive(file_id):
    drive = authenticate_drive()
    file = drive.CreateFile({'id': file_id})
    file.FetchMetadata()

    file_bytes = file.GetContentString(encoding=None).encode('latin1')
    file_content = io.BytesIO(file_bytes)
    return Dataset('inmemory.nc', mode='r', memory= file_content.read())

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
    if 'RH' in nc.variables:
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

def get_rainfall(ncfile, timeidx):
    rainnc = getvar(ncfile, "RAINNC", timeidx=timeidx)
    rainc = getvar(ncfile, "RAINC", timeidx=timeidx) if "RAINC" in ncfile.variables else 0
    return rainnc + rainc  # Total rainfall

def get_temperature(ncfile, timeidx, level=None):
    if level:  # pressure-level temperature
        theta = getvar(ncfile, "T", timeidx=timeidx)  # Potential temperature
        p = getvar(ncfile, "pressure", timeidx=timeidx)
        
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
        return getvar(ncfile, "T2", timeidx=timeidx) - 273.15
    
def get_humidity(ncfile, timeidx, level=None):
    if level:  # pressure-level RH
        rh = getvar(ncfile, "RH", timeidx=timeidx)
        p = getvar(ncfile, "pressure", timeidx=timeidx)
        return interplevel(rh, p, level)
    else:
        if "RH2" in ncfile.variables:
            return getvar(ncfile, "RH2", timeidx=timeidx)
        elif "Q2" in ncfile.variables:
            return getvar(ncfile, "Q2", timeidx=timeidx) * 1000  # Convert to g/kg
        else:
            return None

def get_pressure(ncfile, timeidx):
    return getvar(ncfile, "pressure", timeidx=timeidx)

def get_wind_speed(ncfile, timeidx, level=None):
    """
    Returns wind speed magnitude at surface (10m) or pressure level.
    """
    if level:  # pressure-level wind speed
        u = getvar(ncfile, "U", timeidx=timeidx)
        v = getvar(ncfile, "V", timeidx=timeidx)
        p = getvar(ncfile, "pressure", timeidx=timeidx)
        u_interp = interplevel(u, p, level)
        v_interp = interplevel(v, p, level)
        return (u_interp**2 + v_interp**2)**0.5
    else:
        u10 = getvar(ncfile, "U10", timeidx=timeidx)
        v10 = getvar(ncfile, "V10", timeidx=timeidx)
        return (u10**2 + v10**2)**0.5
