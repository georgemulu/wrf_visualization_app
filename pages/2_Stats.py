import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from dateutil.parser import parse
from scipy import stats
from config import R2_PUBLIC_URL
from data_loader import load_wrf_data, get_available_variables
from wrf import getvar, ALL_TIMES
from metpy.plots import SkewT
from metpy.units import units
import metpy.calc as mpcalc

# --------------------------
# Page Configuration
# --------------------------
st.set_page_config(
    page_title="Weather Analytics",
    page_icon="🌦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS Styling
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
nc = load_wrf_data(R2_PUBLIC_URL)

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
            filtered_vars = [v for v in available_vars if v[0] !='Temperature' and 'Wind Speed' not in v[0]]
            selected_var_name = st.selectbox("📊 Select Variable", [v[0] for v in filtered_vars])
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
    
    # Generate sample data 
    time_points = np.arange(len(time_strs))
    current_data = 10 * np.sin(time_points/10) + 15 + np.random.normal(0, 2, len(time_strs))
    
    # --------------------------
    # Data Visualization Section
    # --------------------------
    st.header("📊 DATA VISUALIZATION")

    # Add a tab system to organize plots
    tab1, tab2, tab3 = st.tabs(["Time Series", "Distributions", "Thermodynamic Analysis"])
    
    with tab1:
        # Main Time Series Plot
        with st.container():

            fig, ax = plt.subplots(figsize=(14, 6))

            # Convert time strings to datetime objects for plotting
            time_dates = [parse(t) for t in time_strs]

            ax.plot(time_dates, current_data, color='#1f77b4', linewidth=2)
            
            # Add trend line
            time_points = np.arange(len(time_dates))
            z = np.polyfit(time_points, current_data, 1)
            p = np.poly1d(z)
            ax.plot(time_dates, p(time_points), "r--", label=f'Trend ({z[0]:.2f} units/hr)')
            
            ax.set_title(f"{selected_var_name} Time Series", fontsize=14, pad=15)
            # ax.set_xlabel("Time", fontsize=12)
            ax.set_ylabel(f"{selected_var_name} (units)", fontsize=12)

            # Format x-axis to show dates 
            ax.set_xticks(time_dates)  # Force all timestamps to be shown
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))

            # Rotate and align the tick labels
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right', rotation_mode='anchor')
            
            # Adjust margins to prevent label cutoff
            plt.subplots_adjust(bottom=0.2)
            
            ax.grid(True, alpha=0.3)
            ax.legend()
            st.pyplot(fig)

    with tab2:
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

    with tab3:
        st.header("🌡 Atmospheric Profile (Skew-T)")
    
        try:
            # 1. Get raw variables with explicit unit conversion
            p = units.Quantity(nc.variables['P'][time_idx,:,:,:] + nc.variables['PB'][time_idx,:,:,:], 'Pa')
            t = units.Quantity(nc.variables['T'][time_idx,:,:,:] + 300.0, 'K')
            qv = units.Quantity(nc.variables['QVAPOR'][time_idx,:,:,:], 'kg/kg')
            
            # 2. Select grid point
            i, j = t.shape[1]//2, t.shape[2]//2
            
            # 3. Extract 1D profiles (maintain units)
            pressure = p[:,i,j]
            temperature = t[:,i,j]
            qvapor = qv[:,i,j]
            
            # 4. Verify units
            assert pressure.units == units.Pa, "Pressure has wrong units"
            assert temperature.units == units.K, "Temperature has wrong units"
            assert qvapor.units == units('kg/kg'), "QVAPOR has wrong units"
            
            # 5. Calculate dewpoint
            dewpoint = mpcalc.dewpoint_from_specific_humidity(
                pressure, 
                temperature,
                qvapor
            )
            
            # 6. Create Skew-T plot
            fig = plt.figure(figsize=(10, 10))
            skew = SkewT(fig, rotation=45)
            
            # 7. Plot data (convert temp to °C for display)
            skew.plot(pressure, temperature.to('degC'), 'r', label='Temperature')
            skew.plot(pressure, dewpoint, 'g', label='Dewpoint')
            
            # 8. Add thermodynamic lines
            skew.plot_dry_adiabats()
            skew.plot_moist_adiabats()
            skew.plot_mixing_lines()
            
            # 9. Calculate parcel profile
            parcel = mpcalc.parcel_profile(pressure, temperature[0], dewpoint[0])
            skew.plot(pressure, parcel.to('degC'), 'k--', label='Parcel Path')
            
            # 10. Calculate indices
            cape, cin = mpcalc.cape_cin(pressure, temperature, dewpoint, parcel)
            lcl_p, _ = mpcalc.lcl(pressure[0], temperature[0], dewpoint[0])
            
            plt.title(f'Skew-T at {selected_time_str}\n'
                    f'CAPE: {cape.m:.0f} J/kg | CIN: {cin.m:.0f} J/kg | LCL: {lcl_p.m:.0f} hPa',
                    loc='left')
            plt.legend()
            st.pyplot(fig)
            
        except Exception as e:
            st.error(f"Skew-T generation failed: {str(e)}")
            
            # Debug output
            st.write("### Unit Verification:")
            for name, var in [('Pressure', 'p'), ('Temperature', 't'), ('QVAPOR', 'qv')]:
                if var in locals():
                    st.write(f"{name}: {eval(var).units if hasattr(eval(var), 'units') else 'NO UNITS'}")
                else:
                    st.write(f"{name}: Not loaded")
    # --------------------------
    # Statistical Analysis
    # --------------------------
    st.header("🧮 STATISTICAL ANALYSIS")
    
    stats_metrics = [
        ("📉 Minimum", np.min(current_data), "Lowest observed value"),
        ("📈 Maximum", np.max(current_data), "Highest observed value"),
        ("📊 Mean", np.mean(current_data), "Average value"),
        ("📐 Std Dev", np.std(current_data), "Measure of variability"),
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
    
# Footer
st.markdown("""
<div style="text-align: center; margin-top: 40px; color: #666666; font-size: 12px;">
    Weather Analytics Dashboard • Powered by WRF Model
</div>
""", unsafe_allow_html=True)