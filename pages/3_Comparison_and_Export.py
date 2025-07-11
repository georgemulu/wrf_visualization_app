import streamlit as st
from dateutil.parser import parse
from config import FILE_ID,CMAP_OPTIONS
from data_loader import load_wrf_data, get_available_variables
from wrf import getvar, ALL_TIMES
from plot_utils import create_plot, save_figure

st.title("📑 Forecast Comparison & Export")

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

    col1, col2 = st.columns(2)
    cmap_group = selected_var_name.split(' ')[0] if selected_var_name != 'Relative Humidity' else 'Humidity'
    cmap_options = CMAP_OPTIONS.get(cmap_group)
    selected_cmap = st.selectbox("Select Colormap", cmap_options)
    with col1:
        fig1, _ = create_plot(nc, selected_var_name, time_idx, selected_cmap, pressure_level)
        if fig1:
            st.pyplot(fig1)
            st.caption(f"Current: {selected_time_str}")

    with col2:
        if time_idx < len(time_strs) - 1:
            fig2, _ = create_plot(nc, selected_var_name, time_idx+1, selected_cmap, pressure_level)
            if fig2:
                st.pyplot(fig2)
                st.caption(f"Next: {time_strs[time_idx+1]}")
        else:
            st.info("No future timestep available.")

    if fig1:
        buf = save_figure(fig1)
        clean_time = parse(selected_time_str).strftime("%Y%m%d_%H%M")
        filename = f"{selected_var_name.replace(' ', '_')}_{clean_time}.png"
        st.download_button("Download Current Plot", data=buf, file_name=filename, mime="image/png")