from fastapi import FastAPI
from backend import wrf_api

app = FastAPI(title="WRF Weather API")

app.include_router(wrf_api.router)