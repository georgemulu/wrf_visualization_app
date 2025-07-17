FILE_PATH = r"C:\Users\Hp\wrfout.nc"
COUNTY_SHAPEFILE_PATH = r"C:\Users\Hp\gadm41_KEN_1.shp"
# FILE_PATH = "/home/technerd/wrfout.nc"
# COUNTY_SHAPEFILE_PATH = "/home/technerd/gadm41_KEN_1.shp"
# SUBCOUNTY_SHAPEFILE_PATH = "/home/technerd/gadm41_KEN_shp/gadm41_KEN_2.shp"


STANDARD_PRESSURE_LEVELS = [1000, 850, 700, 500, 300, 200]


CMAP_OPTIONS = {
    'Temperature': ['coolwarm', 'viridis', 'cividis'],
    'Rainfall': ['Blues', 'GnBu', 'coolwarm'],
    'Humidity': ['viridis', 'YlGnBu']
}