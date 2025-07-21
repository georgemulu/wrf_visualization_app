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
from data_loader import (
    get_rainfall,
    get_temperature,
    get_humidity,
    get_pressure,
    get_wind_speed
)

def create_plot(nc, var_type, time_idx=0, cmap='viridis', pressure_level=None):
    fig = plt.figure(figsize=(12, 8), dpi=150)
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_extent([33.5, 42.0, -5.0, 5.5], crs=ccrs.PlateCarree())

    try:
        # === Get Lat/Lon ===
        if '2m' in var_type or '10m' in var_type:
            lats, lons = latlon_coords(getvar(nc, "T2", timeidx=time_idx))
        else:
            lats, lons = latlon_coords(getvar(nc, "T", timeidx=time_idx))

        current_data = None
        label = None

        # === WIND ===
        if 'Wind Speed' in var_type:
            data = get_wind_speed(nc, timeidx=time_idx, level=pressure_level if 'pressure' in var_type else None)
            u, v = None, None

            if '10m' in var_type:
                u = getvar(nc, 'U10', timeidx=time_idx)
                v = getvar(nc, 'V10', timeidx=time_idx)
            else:
                u = getvar(nc, 'U', timeidx=time_idx)
                v = getvar(nc, 'V', timeidx=time_idx)
                u = destagger(u, stagger_dim=-1)
                v = destagger(v, stagger_dim=-2)
                p = getvar(nc, 'pressure', timeidx=time_idx)
                u = interplevel(u, p, pressure_level)
                v = interplevel(v, p, pressure_level)
                wind_speed = np.sqrt(u**2 + v**2)

            # --- DRAW BACKGROUND FEATURES ---
            ax.add_feature(cfeature.OCEAN.with_scale('10m'), facecolor='lightblue')
            ax.add_feature(cfeature.LAKES.with_scale('10m'), facecolor='lightblue', edgecolor='blue')
            ax.add_feature(cfeature.LAND.with_scale('10m'), facecolor='#e0dccd')  # light beige land

            subset = 10
            ax.barbs(to_np(lons[::subset, ::subset]), to_np(lats[::subset, ::subset]),
                    to_np(u[::subset, ::subset]), to_np(v[::subset, ::subset]),
                    length=6, color='black', linewidth=0.5,
                    transform=ccrs.PlateCarree()
                    ) 
            current_data = wind_speed

        # === TEMPERATURE ===
        elif 'Temperature' in var_type:
            if var_type == 'Temperature (2m)':
                temp = getvar(nc, 'T2', timeidx=time_idx) - 273.15
            else:
                tk = getvar(nc, 'tk', timeidx=time_idx) -273.15
                p = getvar(nc, 'pressure', timeidx=time_idx)
                temp = interplevel(tk, p, pressure_level)
            levels = np.linspace(np.min(temp), np.max(temp), 20)
            contour = ax.contourf(lons, lats, temp, levels=levels, cmap=cmap, transform=ccrs.PlateCarree())
            plt.colorbar(contour, ax=ax, label=f'Temperature (°C) at {pressure_level} hPa' if pressure_level else 'Temperature (°C)')
            current_data = temp

        elif var_type == 'Rainfall':
            rain = getvar(nc, 'RAINNC', timeidx=time_idx)
            rain += getvar(nc, 'RAINC', timeidx=time_idx)
            levels = np.linspace(0, 50, 11)
            contour = ax.contourf(lons, lats, rain, levels=levels, cmap=cmap, transform=ccrs.PlateCarree(), extend='max')
            plt.colorbar(contour, ax=ax, label='Rainfall (mm)')
            current_data = rain

        elif  var_type == 'Humidity (2m)':
                    hum2 = getvar(nc, 'Q2', timeidx=time_idx) * 1000
                    label = 'Specific Humidity (g/kg)'
                    levels = np.linspace(0, 20, 11)
                    contour = ax.contourf(lons, lats, hum2, levels=levels, cmap=cmap, transform=ccrs.PlateCarree())
                    plt.colorbar(contour, ax=ax, label=f'{label} at {pressure_level} hPa' if pressure_level else label)
                    current_data = hum2

        elif var_type == 'Relative Humidity':
                rh = getvar(nc, 'rh', timeidx=time_idx)
                p = getvar(nc, 'pressure', timeidx=time_idx)
                hum = interplevel(rh, p, pressure_level)
                label = 'Relative Humidity (%)'
                levels = np.linspace(0, 100, 11)
                contour = ax.contourf(lons, lats, hum, levels=levels, cmap=cmap, transform=ccrs.PlateCarree())
                plt.colorbar(contour, ax=ax, label=f'{label} at {pressure_level} hPa' if pressure_level else label)
                current_data = hum

        # === Background Features ===
        ax.add_feature(cfeature.OCEAN.with_scale('10m'), facecolor='lightblue')
        ax.add_feature(cfeature.LAKES.with_scale('10m'), facecolor='lightblue', edgecolor='blue')
        ax.add_feature(cfeature.LAND.with_scale('10m'), facecolor='#e0dccd')
        ax.add_feature(cfeature.COASTLINE.with_scale('10m'))
        ax.add_feature(cfeature.BORDERS.with_scale('10m'), linestyle=':', edgecolor='gray')
        ax.gridlines(draw_labels=True)

        # === County Boundaries ===
        try:
            counties = ShapelyFeature(Reader(COUNTY_SHAPEFILE_PATH).geometries(), ccrs.PlateCarree(), edgecolor='black', facecolor='none')
            ax.add_feature(counties, linewidth=0.8)
        except Exception as e:
            st.warning(f"Could not load counties: {e}")

        title = f"{var_type} at {pressure_level} hPa" if pressure_level else var_type
        ax.set_title(title, fontsize=16)
        plt.tight_layout()
        return fig, current_data

    except Exception as e:
        st.error(f"Error creating {var_type} plot: {str(e)}")
        return None, None


def summarize_over_county(gdf, sub_gdf, county_name, data, lats, lons):
    import pandas as pd
    from shapely.geometry import Point

    flat_points = []
    for i in range(lats.shape[0]):
        for j in range(lats.shape[1]):
            flat_points.append({
                'lat': float(lats[i, j]),
                'lon': float(lons[i, j]),
                'value': float(data[i, j])
            })
    df = pd.DataFrame(flat_points)
    geometry = gpd.points_from_xy(df['lon'], df['lat'])
    df_gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")

    target_county = gdf[gdf['NAME_1'].str.lower() == county_name.lower()]
    if target_county.empty:
        return None, None

    county_points = df_gdf[df_gdf.within(target_county.geometry.values[0])]
    if county_points.empty:
        return None, None

    stats = {
        'mean': round(county_points['value'].mean(), 2),
        'min': round(county_points['value'].min(), 2),
        'max': round(county_points['value'].max(), 2)
    }

    return stats, county_points


def save_figure(fig):
    from io import BytesIO
    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    return buf
