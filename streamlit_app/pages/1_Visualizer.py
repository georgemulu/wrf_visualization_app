import numpy as np
import streamlit as st
import requests
from config import STANDARD_PRESSURE_LEVELS, CMAP_OPTIONS
from plot_utils import render_map

st.title("Visualizer")
var_name = st.selectbox("Select Variable", ["Rainfall", "Temperature", "Humidity"])
time_idx = st.slider("Time Index", 0, 10, 0)
level = st.selectbox("Pressure Level", STANDARD_PRESSURE_LEVELS)
cmap = st.selectbox("Colormap", CMAP_OPTIONS[var_name])

with st.spinner("Loading data ..."):
    response = requests.get("http://localhost:8000/data", params={
        "var_name": var_name,
        "time_idx": time_idx,
        "level": level
    })
    if response.status_code == 200:
        data = np.array(response.json()['data'])
        fig = render_map(data, title=f"{var_name} at T={time_idx}", cmap=cmap)
        st.pyplot(fig)
    else:
        st.error("Failed to Load data from backend. ")
