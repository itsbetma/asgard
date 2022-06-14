import datetime
from json import JSONDecodeError

import numpy as np
from typing import Union

from fastapi import FastAPI, Request

routes = FastAPI()

consumption_counter = 0
consumption_increment = 0.1
last_time = datetime.datetime.utcnow()


@routes.get("/")
def read_root():
    return {"Heimdall": "Welcome do Asgard"}


@routes.get("/consumption/{device}/")
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


@routes.get("/incremental/")
def read_item():
    global consumption_counter, last_time
    return dict(consumption=consumption_counter, consumption_increment=consumption_increment,
                unit="kW per minutes")


@routes.post("/incremental/set")
async def incremental_set(info: Request):
    global consumption_counter, consumption_increment
    try:
        request_info = await info.json()
    except JSONDecodeError as e:
        return dict(message="JSON object is missing or may be defined in a way that is not considered a JSON.")
    if "increment" not in request_info:
        return dict(info=request_info, message="Key increment is missing.")
    consumption_increment = request_info['increment']
    return dict(consumption=consumption_counter, info=request_info, consumption_increment=consumption_increment,
                unit="kW per minutes")


@routes.get("/incremental/reset/")
def read_item():
    global consumption_counter, consumption_increment
    consumption_counter = 0
    consumption_increment = 0.1
    return dict(consumption=consumption_counter, consumption_increment=consumption_increment,
                unit="kW per minutes")


@routes.get("/incremental/now")
def read_item():
    global consumption_counter, consumption_increment, last_time
    time_now = datetime.datetime.utcnow()
    seconds = (time_now - last_time).seconds
    for i in range(seconds):
        consumption_counter += consumption_increment
    last_time = time_now
    return dict(consumption=consumption_counter, amount_of_seconds=seconds, consumption_increment=consumption_increment, unit="kW per minutes")
