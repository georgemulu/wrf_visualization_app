import xarray as xr
import fsspec
from streamlit_app.config import R2_PUBLIC_URL

_ds_cache = None

def load_wrf_data():
    global _ds_cache
    if _ds_cache is None:
        fs = fsspec.filesystem("http")
        with fs.open(R2_PUBLIC_URL) as f:
            _ds_cache = xr.open_dataset(f, engine="h5netcdf")
            return _ds_cache
