from netCDF4 import Dataset
import streamlit as st
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
    temp_path = "temp.nc"
    file.GetContentFile(temp_path)
    return Dataset(temp_path)

def get_available_variables(nc):
    available = []
    if all(var in nc.variables for var in ['U10', 'V10']):
        available.append(('Wind Speed (10m)', 'surface'))
    if 'T2' in nc.variables:
        available.append(('Temperature (2m)', 'surface'))
    if 'RAINNC' in nc.variables:
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