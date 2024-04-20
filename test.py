import pandas as pd
from fastapi import FastAPI

df = pd.read_csv("DisasterDeclarationsSummaries.csv")

def get_disaster_data(disType):
    data = {}
    for index, row in df.iterrows():
        incidentType = row['incidentType']
        state = row['state']
        if incidentType == disType:
            if state not in data.keys():
                data[state] = 1
            else:
                data[state] += 1
    return data

def get_snow_ice_storm():
    data = {}
    for index, row in df.iterrows():
        incidentType = row['incidentType']
        state = row['state']
        if incidentType == "Snowstorm" or incidentType == "Severe Ice Storm":
            if state not in data.keys():
                data[state] = 1
            else:
                data[state] += 1
    return data

app = FastAPI()

@app.get("/flood_data")
def get_flood():
    return get_disaster_data("Flood")

@app.get("/fire_data")
def get_fire():
    return get_disaster_data("Fire")

@app.get("/hurricane_data")
def get_hurricane():
    return get_disaster_data("Hurricane")

@app.get("/mudslide_data")
def get_hurricane():
    return get_disaster_data("Mud/Landslide")

@app.get("/tornado_data")
def get_tornado():
    return get_disaster_data("Tornado")

@app.get("/drought_data")
def get_drought():
    return get_disaster_data("Drought")

@app.get("/earthquake_data")
def get_flood():
    return get_disaster_data("Earthquake")

@app.get("/snowstorm_data")
def get_flood():
    return get_snow_ice_storm()
