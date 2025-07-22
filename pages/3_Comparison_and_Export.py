import streamlit as st
import pandas as pd
import io
from dateutil.parser import parse
from config import CMAP_OPTIONS,CMAP_OPTIONS, R2_PUBLIC_URL
from data_loader import load_wrf_data, get_available_variables
from wrf import getvar, ALL_TIMES
from plot_utils import create_plot, save_figure, summarize_over_county
import numpy as np


# == App Title ==
st.title("🆚 Forecast Comparison Mode")

# ==Load NetCDF4 Data ==
nc = load_wrf_data(R2_PUBLIC_URL)

if nc:
    # == Load Available Varibles ==
    available_vars, pressure_levels = get_available_variables(nc)
    var_names = [v[0] for v in available_vars]
    selected_var_name = st.selectbox("Select Variable", var_names)
    var_type = next(v[1] for v in available_vars if v[0] == selected_var_name)

    # ==Load the time steps ==
    times = getvar(nc, 'times', timeidx=ALL_TIMES)
    time_strs = [parse(str(t)).strftime("%Y-%m-%d %H:%M") for t in times.values]

    col1, col2 = st.columns(2)
    with col1:
      selected_time_str1 = st.selectbox("Select Time Step 1", time_strs, key="time1")
      time_idx = time_strs.index(selected_time_str1)
    with col2:
        selected_time_str2 = st.selectbox("Select Time Step 2", time_strs, key="time2")
        time_idx = time_strs.index(selected_time_str2)

    # == Load pressure level if needed ==    
    pressure_level = None
    if var_type == 'pressure':
        pressure_level = st.selectbox("📉 Select Pressure Level", pressure_levels)

    # === Select Colormap ===
    cmap_group = selected_var_name.split(' ')[0] if selected_var_name != 'Relative Humidity' else 'Humidity'
    cmap_options = CMAP_OPTIONS.get(cmap_group, ["viridis"])
    selected_cmap = st.selectbox("🎨 Select Colormap", cmap_options)

    # === Plotting ===
    col3, col4 = st.columns(2)
    with col3:
        fig1, field1 = create_plot(nc, selected_var_name, time_idx, selected_cmap, pressure_level)
        if fig1:
            st.pyplot(fig1)
            st.caption(f"🕐 Time Step 1:{selected_time_str1}")

    with col2:
        if time_idx < len(time_strs) - 1:
            fig2, _ = create_plot(nc, selected_var_name, time_idx, selected_cmap, pressure_level)
            if fig2:
                st.pyplot(fig2)
                st.caption(f"🕐 Time Step 2: {selected_time_str2}")
        else:
            st.info("No future timestep available.")

    if fig1:
        buf = save_figure(fig1)
        clean_time = parse(selected_time_str2).strftime("%Y%m%d_%H%M")
        filename = f"{selected_var_name.replace(' ', '_')}_{clean_time}.png"
        st.download_button("🖼️ Download Time Step 2 Plot", data=buf, file_name=filename, mime="image/png")
