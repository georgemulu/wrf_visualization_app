FILE_PATH = "https://pub-b751f3e6a8f143ca9b0f72a9a0fb0235.r2.dev/wrfout.nc"
COUNTY_SHAPEFILE_PATH = "data/gadm41_KEN_1.shp"
SUBCOUNTY_SHAPEFILE_PATH = "data\gadm41_KEN_2.shp"
# FILE_PATH = "/home/technerd/wrfout.nc"
# COUNTY_SHAPEFILE_PATH = "/home/technerd/gadm41_KEN_1.shp"
# SUBCOUNTY_SHAPEFILE_PATH = "/home/technerd/gadm41_KEN_shp/gadm41_KEN_2.shp"


STANDARD_PRESSURE_LEVELS = [1000, 850, 700, 500, 300, 250]


CMAP_OPTIONS = {
    'Temperature': ['coolwarm', 'viridis', 'cividis'],
    'Rainfall': ['Blues', 'GnBu', 'coolwarm'],
    'Humidity': ['viridis', 'YlGnBu']
}