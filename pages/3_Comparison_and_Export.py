import streamlit as st
import pandas as pd
import io
from dateutil.parser import parse
from config import CMAP_OPTIONS,CMAP_OPTIONS, R2_PUBLIC_URL
from data_loader import load_wrf_data_from_r2, get_available_variables
from wrf import getvar, ALL_TIMES
from plot_utils import create_plot, save_figure, summarize_over_county
import numpy as np


# == App Title ==
st.title("🆚 Forecast Comparison Mode")

# ==Load NetCDF4 Data ==
nc , xr_ds = load_wrf_data_from_r2()

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
      time_idx1 = time_strs.index(selected_time_str1)
    with col2:
        selected_time_str2 = st.selectbox("Select Time Step 2", time_strs, key="time2")
        time_idx2 = time_strs.index(selected_time_str2)

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
        fig1, field1 = create_plot(nc, selected_var_name, time_idx1, selected_cmap, pressure_level)
        if fig1:
            st.pyplot(fig1)
            st.caption(f"🕐 Time Step 1:{selected_time_str1}")

    with col4:
            fig2, field2 = create_plot(nc, selected_var_name, time_idx2, selected_cmap, pressure_level)
            if fig2:
                st.pyplot(fig2)
                st.caption(f"🕐 Time Step 2:{selected_time_str2}")

    if fig1 and fig2:
        selected_plot = st.selectbox("🖼️ Choose Plot to Download", ["Time Step 1", "Time Step 2"])
        
        if selected_plot =="Time Step 1":
            buf = save_figure(fig1)
            clean_time = parse(selected_time_str1).strftime("%Y%m%d_%H%M")
        else:
            buf = save_figure(fig2)
            clean_time = parse(selected_time_str2).strftime("%Y%m%d_%H%M")   
        filename = f"{selected_var_name.replace(' ', '_')}_{clean_time}.png"

        st.download_button(
            label=f"⬇️ Download {selected_plot} Plot",
            data=buf,
            file_name=filename,
            mime="image/png"
        )
