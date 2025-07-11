import streamlit as st
import numpy as np
from dateutil.parser import parse
from config import FILE_ID
from data_loader import load_wrf_data, get_available_variables
from wrf import getvar, ALL_TIMES
from plot_utils import create_plot

st.title("📊 Variable Stats & Anomaly Detection")

nc = load_wrf_data(FILE_ID)
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
    if var_type == 'pressure':
        pressure_level = st.selectbox("Select Pressure Level", pressure_levels)

    fig, current_data = create_plot(nc, selected_var_name, time_idx, 'viridis', pressure_level)

    if current_data is not None:
        st.subheader("📈 Statistics")
        st.metric("Minimum", f"{np.nanmin(current_data):.2f}")
        st.metric("Maximum", f"{np.nanmax(current_data):.2f}")
        st.metric("Mean", f"{np.nanmean(current_data):.2f}")
        st.metric("Standard Deviation", f"{np.nanstd(current_data):.2f}")

        st.subheader("⚠️ Anomaly Detection")
        if 'Temperature' in selected_var_name and (pressure_level == 850 or var_type == 'surface'):
            climatology = 12.5 if pressure_level == 850 else 25.0
            anomaly = np.nanmean(current_data) - climatology
            if abs(anomaly) > 5:
                st.warning(f"Extreme anomaly: {anomaly:.1f}°C deviation from climatology")
            elif abs(anomaly) > 2:
                st.info(f"Mild anomaly: {anomaly:.1f}°C deviation from climatology")
            else:
                st.success("No significant anomaly detected.")
        else:
            st.write("Anomaly detection is only enabled for temperature at surface or 850hPa.")
    else:
        st.error("Unable to compute statistics due to plot error.")