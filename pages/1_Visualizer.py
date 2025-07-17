import streamlit as st
from config import FILE_PATH, CMAP_OPTIONS,STANDARD_PRESSURE_LEVELS
from data_loader import load_wrf_data, get_available_variables
from wrf import getvar, ALL_TIMES
from dateutil.parser import parse
from plot_utils import create_plot

st.title("📡 WRF Variable Visualizer")

nc = load_wrf_data(FILE_PATH)
if nc:
    available_vars, pressure_levels = get_available_variables(nc)
    times = getvar(nc, 'times', timeidx=ALL_TIMES)
    time_strs = [parse(str(t)).strftime("%Y-%m-%d %H:%M") for t in times.values]
    selected_time_str = st.selectbox("Select Time", time_strs)
    time_idx = time_strs.index(selected_time_str)

    var_names = [v[0] for v in available_vars]
    selected_var_name = st.selectbox("Select Variable", var_names)
    var_type = next(v[1] for v in available_vars if v[0] == selected_var_name)

    pressure_level = None
    if 'Wind Speed' in selected_var_name:
        allowed_levels=[850, 700, 250]
    else:
        allowed_levels = [STANDARD_PRESSURE_LEVELS]

    level_options = [lvl for lvl in pressure_levels if lvl in allowed_levels]
    if var_type == 'pressure':
        pressure_level = st.selectbox("Select Pressure Level", level_options)

    cmap_group = selected_var_name.split(' ')[0]
    cmap = st.selectbox("Colormap", CMAP_OPTIONS.get(cmap_group))

    fig, _ = create_plot(nc, selected_var_name, time_idx, cmap, pressure_level)
    if fig:
        st.pyplot(fig)
    else:
        st.error("Plot generation failed.")