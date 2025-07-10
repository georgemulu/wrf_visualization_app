# 🌍 WRF Data Visualization Portal - Kenya

This is a multi-page Streamlit application for visualizing meteorological data from WRF (Weather Research and Forecasting) model output over Kenya.

---

## 📦 Features

- Visualize WRF variables such as:
  - Wind Speed (10m & pressure levels)
  - Temperature (2m & pressure levels)
  - Rainfall
  - Humidity (Specific/Relative)
- Overlay Kenyan county boundaries for context.
- Customize colormap and pressure levels.
- Display statistics (min, max, mean, std) for selected variables.
- Detect anomalies in temperature values compared to a basic climatology.
- Compare two consecutive time steps side-by-side.
- Export generated plots as PNG.

---

## 📁 App Structure

wrf_visualization_app/
├── app.py # Main launcher page
├── config.py # Configuration (paths, colormaps, etc.)
├── data_loader.py # Functions to load WRF and shapefile data
├── plot_utils.py # Plot generation and figure export
├── pages/
│ ├── 1_Visualizer.py # Main variable visualizer
│ ├── 2_Stats_and_Anomalies.py # Statistics and anomaly detection
│ └── 3_Comparison_and_Export.py # Time comparison and image export
└── .streamlit/
└── config.toml # Streamlit theme customization


---

## 🛠️ Requirements

- Python 3.8+
- Streamlit
- wrf-python
- netCDF4
- matplotlib
- cartopy
- geopandas
- numpy
- python-dateutil

Install dependencies using:

pip install -r requirements.txt

🚀 Running the App

cd wrf_visualization_app
streamlit run app.py

Make sure to:

Update the FILE_PATH and COUNTY_SHAPEFILE_PATH in config.py to your local dataset and shapefile paths.

Confirm the NetCDF file is a valid WRF output file.

📍 Note
This app is designed for WRF outputs specific to Kenya and includes built-in handling of pressure-level variables and 2D surface values. Customize the anomaly logic or styling further as needed.

📧 Support
For help or feature requests, feel free to open an issue or reach out.