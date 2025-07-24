import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np

def render_map(data, title="", cmap="viridis"):
    fig = plt.figure(figsize=(8, 6))
    ax = plt.axes(projection = ccrs.PlateCarree())
    ax.coastlines()
    ax.add_feature(cfeature.BORDERS)
    ax.set_title(title)
    img = ax.imshow(data, cmap=cmap, origin='lower')
    plt.colorbar(img, ax=ax, shrink=0.6)
    return fig