from netCDF4 import Dataset
from wrf import getvar
import streamlit as st
from config import STANDARD_PRESSURE_LEVELS

def load_wrf_data(file_path):
    try:
        return Dataset(file_path)
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None

def get_available_variables(nc):
    available = []
    if all(var in nc.variables for var in ['U10', 'V10']):
        available.append(('Wind Speed (10m)', 'surface'))
    if 'T2' in nc.variables:
        available.append(('Temperature (2m)', 'surface'))
    if 'RAINNC' in nc.variables or 'RAINC' in nc.variables:
        available.append(('Rainfall', 'surface'))
    if 'Q2' in nc.variables or 'RH2' in nc.variables:
        available.append(('Humidity (2m)', 'surface'))
    if all(var in nc.variables for var in ['U', 'V']):
        available.append(('Wind Speed', 'pressure'))
    if all(var in nc.variables for var in ['tk', 'T']):
        available.append(('Temperature', 'pressure'))
    if 'RH' in nc.variables:
        available.append(('Relative Humidity', 'pressure'))

    return available, STANDARD_PRESSURE_LEVELS.copy()