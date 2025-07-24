from fastapi import APIRouter, Query
from backend.data_loader import load_wrf_data
from backend.wrf_utils import extract_variable

router = APIRouter()

@router.get("/data")
def get_weather_variable(
    var_name: str = Query(..., description="Variable name e.g, Rainfall, Temperature"),
    time_idx: int = 0, 
    level: int = 850
):
    nc = load_wrf_data()
    data = extract_variable(nc, var_name, time_idx, level)
    return{"data": data.tolist()}