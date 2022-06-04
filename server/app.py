import numpy as np
from typing import Union

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"Heimdall": "Welcome do Asgard"}


@app.get("/consumption/{device}/")
def read_item(device: str, amt: Union[int, None] = None):
    amount = 15  # 15 minutes
    low, high = 0, 0
    if amt:
        amount = amt
    if device == 'shower':
        # regular shower uses 5kWh, 0.083kW Minutes
        low, high = 70, 83
    if device == 'air_conditioner':
        # regular shower uses 1.4kWh, 0.023kW Minutes
        low, high = 18, 23
    if device == 'heater':
        # regular heater of 1500W uses 1.5kWh, 0.025kW Minutes
        low, high = 20, 25
    consumption = np.random.randint(low=low, high=high, size=amount)
    consumption = np.round(consumption * 0.001, decimals=3)
    return dict(consumption=consumption.tolist(), unit="kW per minutes")
