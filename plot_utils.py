import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
import geopandas as gpd
from wrf import getvar, interplevel, destagger, latlon_coords, to_np
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature
import streamlit as st
from config import COUNTY_SHAPEFILE_PATH

def create_plot(nc, var_type, time_idx=0, cmap='viridis', pressure_level=None):
    fig = plt.figure(figsize=(12, 8), dpi=150)
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_extent([33.5, 42.0, -5.0, 5.5], crs=ccrs.PlateCarree())

    try:
        if var_type == 'Wind Speed (10m)' or var_type == 'Temperature (2m)':
            lats, lons = latlon_coords(getvar(nc, "T2", timeidx=time_idx))
        else:
            lats, lons = latlon_coords(getvar(nc, "T", timeidx=time_idx))

        if 'Wind Speed' in var_type:
            if var_type == 'Wind Speed (10m)':
                u = getvar(nc, 'U10', timeidx=time_idx)
                v = getvar(nc, 'V10', timeidx=time_idx)
                wind_speed = np.sqrt(u**2 + v**2)
            else:
                u_stag = getvar(nc, 'U', timeidx=time_idx)
                v_stag = getvar(nc, 'V', timeidx=time_idx)
                u = destagger(u_stag, stagger_dim=-1)
                v = destagger(v_stag, stagger_dim=-2)
                p = getvar(nc, 'pressure', timeidx=time_idx)
                u = interplevel(u, p, pressure_level)
                v = interplevel(v, p, pressure_level)
                wind_speed = np.sqrt(u**2 + v**2)

            # --- DRAW BACKGROUND FEATURES ---
            ax.add_feature(cfeature.OCEAN.with_scale('10m'), facecolor='lightblue')
            ax.add_feature(cfeature.LAKES.with_scale('10m'), facecolor='lightblue', edgecolor='blue')
            ax.add_feature(cfeature.LAND.with_scale('10m'), facecolor='#e0dccd')  # light beige land
            
            skip = (slice(None, None, 5), slice(None, None, 5))
            
            ax.barbs(to_np(lons[skip]), to_np(lats[skip]),
                    to_np(u[skip]), to_np(v[skip]),
                    length=6, color='black', linewidth=0.5,
                    transform=ccrs.PlateCarree()
                    )
            current_data = wind_speed

        elif 'Temperature' in var_type:
            if var_type == 'Temperature (2m)':
                temp = getvar(nc, 'T2', timeidx=time_idx) - 273.15
            else:
                tk = getvar(nc, 'tk', timeidx=time_idx)
                p = getvar(nc, 'pressure', timeidx=time_idx)
                temp = interplevel(tk, p, pressure_level) - 273.15
            levels = np.linspace(np.min(temp), np.max(temp), 20)
            contour = ax.contourf(lons, lats, temp, levels=levels, cmap=cmap, transform=ccrs.PlateCarree())
            plt.colorbar(contour, ax=ax, label=f'Temperature (°C) at {pressure_level} hPa' if pressure_level else 'Temperature (°C)')
            current_data = temp

        elif var_type == 'Rainfall':
            rain = getvar(nc, 'RAINNC', timeidx=time_idx)
            levels = np.linspace(0, 50, 11)
            contour = ax.contourf(lons, lats, rain, levels=levels, cmap=cmap, transform=ccrs.PlateCarree(), extend='max')
            plt.colorbar(contour, ax=ax, label='Rainfall (mm)')
            current_data = rain

        elif 'Humidity' in var_type or var_type == 'Relative Humidity':
            if var_type == 'Humidity (2m)':
                if 'Q2' in nc.variables:
                    hum = getvar(nc, 'Q2', timeidx=time_idx) * 1000
                    label = 'Specific Humidity (g/kg)'
                    levels = np.linspace(0, 20, 11)
                else:
                    hum = getvar(nc, 'RH2', timeidx=time_idx)
                    label = 'Relative Humidity (%)'
                    levels = np.linspace(0, 100, 11)
            else:
                rh = getvar(nc, 'RH', timeidx=time_idx)
                p = getvar(nc, 'pressure', timeidx=time_idx)
                hum = interplevel(rh, p, pressure_level)
                label = 'Relative Humidity (%)'
                levels = np.linspace(0, 100, 11)
            contour = ax.contourf(lons, lats, hum, levels=levels, cmap=cmap, transform=ccrs.PlateCarree())
            plt.colorbar(contour, ax=ax, label=f'{label} at {pressure_level} hPa' if pressure_level else label)
            current_data = hum

        ax.add_feature(cfeature.COASTLINE.with_scale('10m'))
        ax.add_feature(cfeature.BORDERS.with_scale('10m'), linestyle=':', edgecolor='gray')
        ax.gridlines(draw_labels=True)

        try:
            gdf = gpd.read_file(COUNTY_SHAPEFILE_PATH)
            counties = ShapelyFeature(Reader(COUNTY_SHAPEFILE_PATH).geometries(), ccrs.PlateCarree(), edgecolor='black', facecolor='none')
            ax.add_feature(counties, linewidth=0.8)
            ax.set_title(f"{var_type} at {pressure_level} hPa" if pressure_level else var_type, fontsize=16)
        except Exception as e:
            st.warning(f"Could not load counties: {e}")

        plt.tight_layout()
        return fig, current_data

    except Exception as e:
        st.error(f"Error creating {var_type} plot: {str(e)}")
        return None, None

def save_figure(fig):
    from io import BytesIO
    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    return buf