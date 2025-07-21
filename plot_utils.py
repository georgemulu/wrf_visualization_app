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

            skip = (slice(None, None, 5), slice(None, None, 5))
            ax.barbs(
                to_np(lons[skip]), to_np(lats[skip]),
                to_np(u[skip]), to_np(v[skip]),
                length=4, color='black', linewidth=0.5,
                transform=ccrs.PlateCarree()
            )
            current_data = data

        # === TEMPERATURE ===
        elif 'Temperature' in var_type:
            try:
                if var_type == 'Temperature (2m)':
                    temp = getvar(nc, 'T2', timeidx=time_idx) - 273.15
                else:
                    if 'T' in nc.variables:
                        temp_var = getvar(nc, 'T', timeidx=time_idx)
                    else:
                            raise ValueError("No temperature variable (tk or T) found")
                        
                    p = getvar(nc, 'pressure', timeidx=time_idx)
                        
                    # Validate pressure data
                    if p is None or np.all(np.isnan(p)):
                        raise ValueError("Invalid pressure data")
                            
                    if pressure_level is None:
                        raise ValueError("Pressure level required for upper-air temperature")
                            
                    valid_range = (np.nanmin(p), np.nanmax(p))
                    if not valid_range[0] <= pressure_level <= valid_range[1]:
                        raise ValueError(f"Pressure level {pressure_level}hPa outside valid range {valid_range}")
                    
                    # Perform interpolation
                    temp = interplevel(temp_var, p, pressure_level) - 273.15
                
                # Create plot
                levels = np.linspace(np.min(temp), np.max(temp), 20)
                contour = ax.contourf(lons, lats, temp, levels=levels, cmap=cmap,
                                    transform=ccrs.PlateCarree())
                plt.colorbar(contour, ax=ax,
                            label=f'Temperature (°C) at {pressure_level} hPa'
                            if pressure_level else 'Temperature (°C)')
                current_data = temp
                
            except Exception as e:
                st.error(f"Temperature plotting failed: {str(e)}")
                return None, None

        elif var_type == 'Rainfall':
            try:
                rain = getvar(nc, 'RAINNC', timeidx=time_idx) if 'RAINNC' in nc.variables else 0
                rain += getvar(nc, 'RAINC', timeidx=time_idx) if 'RAINC' in nc.variables else 0
                # Create plot
                levels = np.linspace(0, 50, 11)
                contour = ax.contourf(lons, lats, rain, levels=levels, cmap=cmap,transform=ccrs.PlateCarree(), extend='max')                  
                plt.colorbar(contour, ax=ax, label='Rainfall (mm)')
                current_data = rain
            except Exception as e:
                st.error(f"Rainfall plotting failed: {str(e)}")
                return None, None

        # === HUMIDITY ===
        elif 'Humidity' in var_type or var_type == 'Relative Humidity':
            data = get_humidity(nc, time_idx, level=pressure_level if 'pressure' in var_type else None)
            if 'Q2' in nc.variables and var_type == 'Humidity (2m)':
                label = 'Specific Humidity (g/kg)'
                levels = np.linspace(0, 20, 11)
            else:
                label = 'Relative Humidity (%)'
                levels = np.linspace(0, 100, 11)
            contour = ax.contourf(lons, lats, data, levels=levels, cmap=cmap, transform=ccrs.PlateCarree())
            plt.colorbar(contour, ax=ax, label=f'{label} at {pressure_level} hPa' if pressure_level else label)
            current_data = data

        # === Background Features ===
        ax.add_feature(cfeature.OCEAN.with_scale('10m'), facecolor='lightblue')
        ax.add_feature(cfeature.LAKES.with_scale('10m'), facecolor='lightblue', edgecolor='blue')
        ax.add_feature(cfeature.LAND.with_scale('10m'), facecolor='#e0dccd')
        ax.add_feature(cfeature.COASTLINE.with_scale('10m'))
        ax.add_feature(cfeature.BORDERS.with_scale('10m'), linestyle=':', edgecolor='gray')
        ax.gridlines(draw_labels=True)

        # === County Boundaries ===
        try:
            gdf = gpd.read_file(COUNTY_SHAPEFILE_PATH)
            counties = ShapelyFeature(Reader(COUNTY_SHAPEFILE_PATH).geometries(), ccrs.PlateCarree(), edgecolor='black', facecolor='none')
            ax.add_feature(counties, linewidth=0.8)
            # Add county names at centroids
            # for _, row in gdf.iterrows():
            #     centroid = row.geometry.centroid
            #     county_name = row.get('NAME_1') or row.get('NAME')  # Adjust to actual column name
            #     if county_name:
            #         ax.text(
            #             centroid.x, centroid.y, county_name,
            #             fontsize=6, color='black', weight='normal',
            #             transform=ccrs.PlateCarree(), ha='center', va='center'
            #         )
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
