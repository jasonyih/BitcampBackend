import pandas as pd
import matplotlib
matplotlib.use('AGG')
import matplotlib.pyplot as plt
from datetime import datetime
import io
from PIL import Image
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware

disasters = pd.read_csv("DisasterDeclarationsSummaries.csv")
mortgages = pd.read_csv("StateMortgagesPercent-30-89DaysLate-thru-2023-09.csv")

state_codes = {
    "AL": "Alabama",
    "AK": "Alaska",
    "AZ": "Arizona",
    "AR": "Arkansas",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DE": "Delaware",
    "FL": "Florida",
    "GA": "Georgia",
    "HI": "Hawaii",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "IA": "Iowa",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "ME": "Maine",
    "MD": "Maryland",
    "MA": "Massachusetts",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MS": "Mississippi",
    "MO": "Missouri",
    "MT": "Montana",
    "NE": "Nebraska",
    "NV": "Nevada",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NY": "New York",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PA": "Pennsylvania",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VT": "Vermont",
    "VA": "Virginia",
    "WA": "Washington",
    "WV": "West Virginia",
    "WI": "Wisconsin",
    "WY": "Wyoming",
}

def get_disaster_data(disType):
    data = {}
    for index, row in disasters.iterrows():
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
    for index, row in disasters.iterrows():
        incidentType = row['incidentType']
        state = row['state']
        if incidentType == "Snowstorm" or incidentType == "Severe Ice Storm":
            if state not in data.keys():
                data[state] = 1
            else:
                data[state] += 1
    return data

def get_df_based_on_date(state, begin_date):
    date_t = datetime.strptime(begin_date, "%Y-%m")
    end_date = date_t.replace(year=date_t.year + 1).strftime("%Y-%m")
    new_df = pd.DataFrame()
    row = mortgages[mortgages['Name'] == state]
    for column in row.columns:
        if column >= begin_date and column <= end_date:
            new_df[column] = row[column]
    
    return new_df

def mortgage_data_for_state(state, date):
    date_t = datetime.strptime(date, "%Y-%m")
    end_date = date_t.replace(year=date_t.year + 1).strftime("%Y-%m")
    data = [
        ["Date", state]
    ]
    
    row = mortgages[mortgages['Name'] == state_codes[state]]
    for column in row.columns:
        if column >= date and column <= end_date:
            index = row[column].keys()[0]
            data.append([column, row[column][index]])
    
    return data

def disaster_list(state, disaster):
    dis_list = {"list": []}
    for index, row in disasters.iterrows():
        if row['incidentBeginDate'] >= "2010" and row['incidentType'] == disaster and row['state'] == state:
            date = row['incidentBeginDate']
            dis_list["list"].append({"state": row['state'], "incidentType": row['incidentType'], "date": date[:date.index("T")]})
    
    return dis_list

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1:5500"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
def get_mudslide():
    return get_disaster_data("Mud/Landslide")

@app.get("/tornado_data")
def get_tornado():
    return get_disaster_data("Tornado")

@app.get("/drought_data")
def get_drought():
    return get_disaster_data("Drought")

@app.get("/earthquake_data")
def get_eq():
    return get_disaster_data("Earthquake")

@app.get("/snowstorm_data")
def get_snowstorm():
    return get_snow_ice_storm()

@app.get("/{state}/{disaster}")
def return_list(state: str, disaster: str):
    return disaster_list(state, disaster)

@app.get("/{state}/{disaster}/{date}")
def return_graph_data(state: str, disaster: str, date: str):
    return mortgage_data_for_state(state, date)
    # df = get_df_based_on_date(state, date)
    # img_bytes = make_graph(df)

    # return Response(content=img_bytes.getvalue(), media_type="image/png")
