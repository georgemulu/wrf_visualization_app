import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from dateutil.parser import parse
from scipy import stats
from config import FILE_ID
from data_loader import load_wrf_data, get_available_variables
from wrf import getvar, ALL_TIMES

# --------------------------
# Page Configuration
# --------------------------
st.set_page_config(
    page_title="Weather Analytics",
    page_icon="🌦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------
# Custom CSS Styling
# --------------------------
st.markdown("""
<style>
    /* Main gradient background */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(to bottom, #f5f7fa, #e4e8ed);
    }
    
    /* Decorative weather icons */
    .weather-icon {
        position: fixed;
        opacity: 0.08;
        z-index: -1;
        font-size: 25vw;
        pointer-events: none;
    }
    #icon1 { top: -10%; right: -5%; }
    #icon2 { bottom: -10%; left: -5%; }
    
    /* Card styling */
    .metric-card {
        background: rgba(255, 255, 255, 0.85);
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        border: 1px solid #e0e0e0;
    }
    
    /* Header styling */
    .gradient-header {
        padding: 15px;
        background: linear-gradient(to right, #4a6fa5, #7db2e5);
        color: white;
        border-radius: 8px;
        margin-bottom: 25px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Plot containers */
    .plot-container {
        background: white;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>

<!-- Dynamic weather icons based on selected variable -->
<div class="weather-icon" id="icon1">🌤</div>
<div class="weather-icon" id="icon2">📊</div>
""", unsafe_allow_html=True)

# --------------------------
# Header Section
# --------------------------
st.markdown("""
<div class="gradient-header">
    <h1 style="margin:0; color:white; text-align:center;">🌦 Weather Analytics Dashboard</h1>
</div>
""", unsafe_allow_html=True)

# --------------------------
# Data Loading
# --------------------------
nc = load_wrf_data(FILE_ID)

if nc:
    # --------------------------
    # Control Panel
    # --------------------------
    with st.expander("⚙ CONTROL PANEL", expanded=True):
        available_vars, pressure_levels = get_available_variables(nc)
        times = getvar(nc, 'times', timeidx=ALL_TIMES)
        time_strs = [parse(str(t)).strftime("%Y-%m-%d %H:%M") for t in times.values]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            selected_time_str = st.selectbox("⏰ Select Time Period", time_strs)
            time_idx = time_strs.index(selected_time_str)
        with col2:
            selected_var_name = st.selectbox("📊 Select Variable", [v[0] for v in available_vars])
        with col3:
            var_type = next(v[1] for v in available_vars if v[0] == selected_var_name)
            pressure_level = st.selectbox("↕ Pressure Level", pressure_levels) if var_type == 'pressure' else None
    
    # Update decorative icons based on selection
    icon_map = {
        'Temperature': '🌡',
        'Humidity': '💧',
        'Wind': '🌪',
        'Pressure': '⏱'
    }
    icon = next((v for k, v in icon_map.items() if k in selected_var_name), '🌤')
    st.markdown(f"""
    <script>
        document.getElementById('icon1').innerHTML = '{icon}';
        document.getElementById('icon2').innerHTML = '{'📈' if var_type == 'surface' else '↕'}';
    </script>
    """, unsafe_allow_html=True)
    
    # Generate sample data (replace with your actual data)
    time_points = np.arange(len(time_strs))
    current_data = 10 * np.sin(time_points/10) + 15 + np.random.normal(0, 2, len(time_strs))
    
    # --------------------------
    # Data Visualization Section
    # --------------------------
    st.header("📊 DATA VISUALIZATION")
    
    # Main Time Series Plot
    with st.container():

        fig, ax = plt.subplots(figsize=(10, 5))

        fig, ax = plt.subplots(figsize=(12, 5))

        ax.plot(time_points, current_data, color='#1f77b4', linewidth=2)
        
        # Add trend line
        z = np.polyfit(time_points, current_data, 1)
        p = np.poly1d(z)
        ax.plot(time_points, p(time_points), "r--", label=f'Trend ({z[0]:.2f} units/hr)')
        
        ax.set_title(f"{selected_var_name} Time Series", fontsize=14, pad=15)
        ax.set_xlabel("Time Index (hours)", fontsize=12)
        ax.set_ylabel(f"{selected_var_name} (units)", fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.legend()
        st.pyplot(fig)
    
    # Distribution Analysis
    col1, col2 = st.columns(2)
    with col1:
        fig2, ax2 = plt.subplots(figsize=(8, 5))
        n, bins, patches = ax2.hist(current_data, bins=20, color='#1f77b4', alpha=0.7)
        
        # Add normal distribution curve
        mu, sigma = np.mean(current_data), np.std(current_data)

        y = ((1 / (np.sqrt(2 * np.pi) * sigma))) * \
        np.exp(-0.5 * ((bins - mu) / sigma)**2) * \
        len(current_data) * (bins[1] - bins[0])

        y = ((1 / (np.sqrt(2 * np.pi) * sigma)) * 
             np.exp(-0.5 * (1 / sigma * (bins - mu))**2) * len(current_data) * (bins[1] - bins[0]))

        ax2.plot(bins, y, 'r--', linewidth=2)
        
        ax2.set_title("Value Distribution", fontsize=14)
        ax2.set_xlabel(f"{selected_var_name} (units)", fontsize=12)
        ax2.set_ylabel("Frequency", fontsize=12)
        ax2.grid(True, alpha=0.3)
        st.pyplot(fig2)
    
    with col2:
        fig3, ax3 = plt.subplots(figsize=(8, 5))
        ax3.boxplot(current_data, vert=False, patch_artist=True,
                   boxprops=dict(facecolor='#1f77b4', alpha=0.7),
                   medianprops=dict(color='red', linewidth=2))
        
        ax3.set_title("Statistical Distribution", fontsize=14)
        ax3.set_xlabel(f"{selected_var_name} (units)", fontsize=12)
        st.pyplot(fig3)
    
    # --------------------------
    # Statistical Analysis
    # --------------------------
    st.header("🧮 STATISTICAL ANALYSIS")
    
    stats_metrics = [
        ("📉 Minimum", np.min(current_data), "Lowest observed value"),
        ("📈 Maximum", np.max(current_data), "Highest observed value"),
        ("📊 Mean", np.mean(current_data), "Average value"),

        ("📐 Std Dev", np.std(current_data), "Measure of variability"),
        ("⟳ Skewness", stats.skew(current_data), "Distribution asymmetry"),
        ("⏏ Kurtosis", stats.kurtosis(current_data), "Tail extremity"),
        ("📌 Median", np.median(current_data), "Middle value"),
        ("📐 Standard Deviation", np.std(current_data), "Measure of variability"),
        ("⟳ Skewness", stats.skew(current_data), "Distribution asymmetry"),
        ("⏏ Kurtosis", stats.kurtosis(current_data), "Tail extremity"),
        ("📌 Median", np.median(current_data), "Middle value"),
        ("🔍 Inter-Quartile Range", stats.iqr(current_data), "Middle 50% range")
    ]
    
    cols = st.columns(4)
    for i, (label, value, help_text) in enumerate(stats_metrics):
        with cols[i % 4]:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size:16px; margin-bottom:5px;">{label}</div>
                <div style="font-size:22px; font-weight:bold; margin-bottom:5px;">{value:.2f}</div>
                <div style="font-size:12px; color:#666666;">{help_text}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # --------------------------
    # Anomaly Detection
    # --------------------------
    if 'Temperature' in selected_var_name and (pressure_level == 850 or var_type == 'surface'):
        st.header("⚠ ANOMALY DETECTION")
        
        climatology = 12.5 if pressure_level == 850 else 25.0
        anomaly = np.mean(current_data) - climatology
        z_score = anomaly / (np.std(current_data) / np.sqrt(len(current_data)))
        
        # Anomaly Visualization
        fig4, ax4 = plt.subplots(figsize=(12, 5))
        ax4.axhspan(climatology-1, climatology+1, facecolor='green', alpha=0.2, label='Normal range')
        ax4.axhspan(climatology-2, climatology+2, facecolor='yellow', alpha=0.2, label='Alert range')
        ax4.plot(time_points, current_data, color='#1f77b4', alpha=0.7)
        ax4.axhline(climatology, color='black', linestyle='--', label='Climatology')
        ax4.axhline(np.mean(current_data), color='red', label='Current mean')
    
        ax4.set_title(f"Temperature Anomaly Detection ({pressure_level or 'surface'} hPa)", fontsize=14)
        ax4.set_xlabel("Time Index")
        ax4.set_ylabel("Temperature (°C)")
        ax4.legend()
        # Enhanced Anomaly Visualization
        fig4, ax4 = plt.subplots(figsize=(12, 5))

        # Improved range colors with better visibility
        ax4.axhspan(climatology-1, climatology+1, 
                facecolor='#4CAF50', alpha=0.3,  # Brighter green
                label='Normal range (±1°C)')
        ax4.axhspan(climatology-2, climatology+2, 
                facecolor='#FFC107', alpha=0.3,  # Brighter amber
                label='Alert range (±2°C)')

        # Extreme range (beyond ±2°C)
        ax4.axhspan(climatology-5, climatology-2, 
                facecolor='#FF5722', alpha=0.1,  # Orange-red
                label='Extreme range')
        ax4.axhspan(climatology+2, climatology+5, 
                facecolor='#FF5722', alpha=0.1)

        # Data and reference lines
        ax4.plot(time_points, current_data, 
                color='#1f77b4', linewidth=2, 
                alpha=0.9, label='Observations')
        ax4.axhline(climatology, 
                color='#333333', linestyle='--', 
                linewidth=2, label='Climatology')
        ax4.axhline(np.mean(current_data), 
                color='#E91E63', linewidth=2, 
                label='Current mean')

        # Styling
        ax4.set_title(f"Temperature Anomaly Detection ({pressure_level or 'surface'} hPa)", 
                    fontsize=14, pad=15)
        ax4.set_xlabel("Time Index (hours)", fontsize=12)
        ax4.set_ylabel("Temperature (°C)", fontsize=12)
        ax4.grid(True, alpha=0.2)
        ax4.legend(loc='upper right', framealpha=1)

        st.pyplot(fig4)
        
        # Anomaly Metrics
        anomaly_cols = st.columns(3)
        with anomaly_cols[0]:
            st.metric("🌡 Climatology", f"{climatology:.1f}°C")
        with anomaly_cols[1]:
            st.metric("🌡 Current Mean", f"{np.mean(current_data):.1f}°C", 
                    delta=f"{anomaly:+.1f}°C", delta_color="inverse")
        with anomaly_cols[2]:
            st.metric("📊 Z-Score", f"{z_score:.2f}σ")
        
        # Interpretation
        if abs(z_score) > 2.58:
            st.error("🚨 Extreme anomaly detected (p < 0.01)")
        elif abs(z_score) > 1.96:
            st.warning("⚠ Significant anomaly detected (p < 0.05)")
        else:
            st.success("✅ No significant anomaly detected")

# --------------------------
# Footer
# --------------------------
st.markdown("""
<div style="text-align: center; margin-top: 40px; color: #666666; font-size: 12px;">
    Weather Analytics Dashboard • Powered by WRF Model
</div>
""", unsafe_allow_html=True)