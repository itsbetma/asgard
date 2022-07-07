import datetime
from json import JSONDecodeError

import numpy as np
from typing import Union

from fastapi import FastAPI, Request, HTTPException

app = FastAPI()

consumption_counter = 0
consumption_increment = 0.1
last_time = datetime.datetime.utcnow()

device_last_time = [
    0,  # Shower
    0,  # Air
    0  # Heater
]

device_consumption = [
    0,  # Shower
    0,  # Air
    0  # Heater
]


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


@app.get("/incremental/")
def read_item():
    global consumption_counter, last_time
    return dict(consumption=consumption_counter, consumption_increment=consumption_increment,
                unit="kW per minutes")


@app.post("/incremental/set")
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


@app.get("/incremental/reset/")
def read_item():
    global consumption_counter, consumption_increment, last_time
    consumption_counter = 0
    consumption_increment = 0.1
    last_time = datetime.datetime.utcnow()
    return dict(consumption=consumption_counter, consumption_increment=consumption_increment,
                unit="kW per minutes")


@app.get("/incremental/now")
def read_item():
    global consumption_counter, consumption_increment, last_time
    time_now = datetime.datetime.utcnow()
    seconds = (time_now - last_time).seconds
    for i in range(seconds):
        consumption_counter += consumption_increment
        consumption_counter = round(consumption_counter, 4)
    last_time = time_now
    return dict(consumption=consumption_counter, amount_of_seconds=seconds, consumption_increment=consumption_increment,
                unit="kW per minutes")


@app.get("/v1/consumption")
def consumption():
    global device_consumption
    minute_base_increase = 0.1
    monthly_consumption = 0
    time_now = datetime.datetime.utcnow()
    day, month, year = time_now.day, time_now.month, time_now.year
    first_day_of_month = datetime.datetime(year, month, day)
    minutes_since_day_one = round((time_now - first_day_of_month).seconds / 60)
    for i in range(minutes_since_day_one):
        monthly_consumption += minute_base_increase
        monthly_consumption = round(monthly_consumption, 4)
    for device in device_consumption:
        monthly_consumption += device
    return dict(monthly_consumption=monthly_consumption, unit="kWh")


@app.get("/v1/consumption/start/{device_param}")
def read_item(device_param: str):
    global device_last_time
    if device_param == 'shower':
        device_last_time[0] = datetime.datetime.utcnow()
    if device_param == 'air_conditioner':
        device_last_time[1] = datetime.datetime.utcnow()
    if device_param == 'heater':
        device_last_time[2] = datetime.datetime.utcnow()
    return dict(device_consumption=device_consumption, device_last_time=device_last_time, unit="kWh")


@app.get("/v1/consumption/end/{device_param}")
def read_item(device_param: str):
    global device_last_time, device_consumption

    if device_param == 'shower':
        if not isinstance(device_last_time[0], datetime.datetime):
            raise HTTPException(status_code=400, detail="It seems that you had not started the consumption.")
        minutes = round((datetime.datetime.utcnow() - device_last_time[0]).seconds / 60)
        device_last_time[0] = 0
        for minute in range(minutes):
            device_consumption[0] += 0.5
    if device_param == 'air_conditioner':
        if not isinstance(device_last_time[1], datetime.datetime):
            raise HTTPException(status_code=400, detail="It seems that you had not started the consumption.")
        minutes = round((datetime.datetime.utcnow() - device_last_time[1]).seconds / 60)
        device_last_time[1] = 0
        for minute in range(minutes):
            device_consumption[1] += 0.5
    if device_param == 'heater':
        if not isinstance(device_last_time[2], datetime.datetime):
            raise HTTPException(status_code=400, detail="It seems that you had not started the consumption.")
        minutes = round((datetime.datetime.utcnow() - device_last_time[2]).seconds / 60)
        device_last_time[2] = 0
        for minute in range(minutes):
            device_consumption[2] += 0.5

    return dict(device_consumption=device_consumption, device_last_time=device_last_time, unit="kWh")
