import streamlit as st
import pandas as pd
import io
from dateutil.parser import parse
from datetime import datetime

from config import FILE_PATH, CMAP_OPTIONS, COUNTY_SHAPEFILE_PATH, SUBCOUNTY_SHAPEFILE_PATH
from data_loader import (
    load_wrf_data,
    get_available_variables,
    load_kenya_shapefiles,
    get_rainfall,
    get_temperature,
    get_humidity,
    get_pressure
)
from wrf import getvar, ALL_TIMES
from plot_utils import create_plot, save_figure, summarize_over_county
import numpy as np

# === App Title ===
st.title("🆚 Forecast Comparison Mode")

# === Load NetCDF Data ===
nc = load_wrf_data(FILE_PATH)

if nc:
    # === Load Available Variables ===
    available_vars, pressure_levels = get_available_variables(nc)
    var_names = [v[0] for v in available_vars]
    selected_var_name = st.selectbox("📌 Select Variable", var_names)
    var_type = next(v[1] for v in available_vars if v[0] == selected_var_name)

    # === Load Time Steps ===
    times = getvar(nc, 'times', timeidx=ALL_TIMES)
    time_strs = [parse(str(t)).strftime("%Y-%m-%d %H:%M") for t in times.values]

    col1, col2 = st.columns(2)
    with col1:
        selected_time_str1 = st.selectbox("🕐 Select Time Step 1", time_strs, key="time1")
    with col2:
        selected_time_str2 = st.selectbox("🕑 Select Time Step 2", time_strs, key="time2")

    time_idx1 = time_strs.index(selected_time_str1)
    time_idx2 = time_strs.index(selected_time_str2)

    # === Pressure Level if needed ===
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
            st.caption(f"🕐 Time Step 1: {selected_time_str1}")

    with col4:
        fig2, field2 = create_plot(nc, selected_var_name, time_idx2, selected_cmap, pressure_level)
        if fig2:
            st.pyplot(fig2)
            st.caption(f"🕑 Time Step 2: {selected_time_str2}")

    # === County Statistics Comparison ===
    st.markdown("### 📊 County Statistics Comparison")
    gdf, sub_gdf = load_kenya_shapefiles(COUNTY_SHAPEFILE_PATH, SUBCOUNTY_SHAPEFILE_PATH)
    county = st.selectbox("🏛️ Select County", gdf["NAME_1"].unique())

    # Latitude and Longitude
    lats = getvar(nc, "XLAT", timeidx=0)
    lons = getvar(nc, "XLONG", timeidx=0)

    if field1 is not None and field2 is not None:
        stats1, _ = summarize_over_county(gdf, sub_gdf, county, field1, lats, lons)
        stats2, _ = summarize_over_county(gdf, sub_gdf, county, field2, lats, lons)

        if stats1 and stats2:
            compare_df = pd.DataFrame({
                "Statistic": ["Mean", "Max", "Min"],
                selected_time_str1: [stats1["mean"], stats1["max"], stats1["min"]],
                selected_time_str2: [stats2["mean"], stats2["max"], stats2["min"]],
            })

            st.dataframe(compare_df, use_container_width=True)

        #     # === Download Stats Button ===
        #     #excel_buf = io.BytesIO()
        #     with pd.ExcelWriter(excel_buf, engine='xlsxwriter') as writer:
        #         compare_df.to_excel(writer, index=False, sheet_name="Comparison_Stats")
        #     excel_buf.seek(0)

        #     st.download_button(
        #         label="📥 Download Comparison Stats",
        #         data=excel_buf.getvalue(),
        #         file_name="comparison_stats.xlsx",
        #         mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        #     )
        # else:
        #     st.warning("No data found within the selected county boundaries.")

    # === Download First Plot ===
    if fig1:
        buf = save_figure(fig1)
        clean_time = parse(selected_time_str1).strftime("%Y%m%d_%H%M")
        filename = f"{selected_var_name.replace(' ', '_')}_{clean_time}.png"
        st.download_button("🖼️ Download Time Step 1 Plot", data=buf, file_name=filename, mime="image/png")
    # === Download Second Plot ===
    if fig2:                    
        buf = save_figure(fig2)
        clean_time = parse(selected_time_str2).strftime("%Y%m%d_%H%M")
        filename = f"{selected_var_name.replace(' ', '_')}_{clean_time}.png"
        st.download_button("🖼️ Download Time Step 2 Plot", data=buf, file_name=filename, mime="image/png")
