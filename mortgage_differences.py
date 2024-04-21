import pandas as pd
from datetime import datetime
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
import json
from scipy.stats import kruskal

disasters = pd.read_csv("DisasterDeclarationsSummaries.csv")
mortgages = pd.read_csv("StateMortgagesPercent-30-89DaysLate-thru-2023-09.csv")
atlanta = pd.read_csv("atlanta.csv")

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
    begin_date = date_t.replace(year=date_t.year - 1).strftime("%Y-%m")
    end_date = date_t.replace(year=date_t.year + 1).strftime("%Y-%m")
    data = [
        ["Date", state_codes[state], {'type': 'string', 'role': 'style'}]
    ]
    
    row = mortgages[mortgages['Name'] == state_codes[state]]
    for column in row.columns:
        if column >= begin_date and column <= end_date:
            index = row[column].keys()[0]
            if column == date:
                data.append([column, row[column][index], 'point { size: 20; shape-type: star; }'])
            else:
                data.append([column, row[column][index], None])
    
    return json.dumps(data)

def foreclosure_for_state(city, date):
    date_t = datetime.strptime(date, "%Y-%m")
    begin_date = date_t.replace(year=date_t.year - 1).strftime("%Y-%m")
    end_date = date_t.replace(year=date_t.year + 1).strftime("%Y-%m")
    data = []

    dates = {}

    for index, row in atlanta.iterrows():
        if not pd.isna(row['Foreclosure_date']):
            foreclosure_date = str(int((row['Foreclosure_date'])))
            date_object = datetime.strptime(foreclosure_date, '%m%Y')
            output = date_object.strftime('%Y-%m')
            if output >= begin_date and output <= end_date:
                if output not in dates.keys():
                    dates[output] = 1
                else:
                    dates[output] += 1
    
    for key in dates.keys():
        data.append([key, dates[key]])
    
    data = sorted(data)
    data.insert(0, ["Date", city])

    return json.dumps(data)

def disaster_list(state, disaster):
    dis_list = {"list": []}
    for index, row in disasters.iterrows():
        if row['incidentBeginDate'] >= "2015" and row['incidentType'] == disaster and row['state'] == state:
            date = row['incidentBeginDate']
            dis_list["list"].append({"state": row['state'], "incidentType": row['incidentType'], "date": date[:date.index("T")]})
    
    return dis_list

def kruskal_wallis(state, date):
    date_t = datetime.strptime(date, "%Y-%m")
    begin_date = date_t.replace(year=date_t.year - 1).strftime("%Y-%m")
    end_date = date_t.replace(year=date_t.year + 1).strftime("%Y-%m")
    row = mortgages[mortgages['Name'] == state_codes[state]]
    data_before = []
    data_after = []
    for column in row.columns:
        if column >= begin_date and column <= date:
            index = row[column].keys()[0]
            data_before.append(row[column][index])
        elif column > date and column <= end_date:
            index = row[column].keys()[0]
            data_after.append(row[column][index])

    results = kruskal(data_before, data_after)
    return results

fires = get_disaster_data("Fire")
floods = get_disaster_data("Flood")
hurricanes = get_disaster_data("Hurricane")

app = FastAPI()

origins = [
     "http://localhost:5173",
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
    return floods

@app.get("/fire_data")
def get_fire():
    return fires

@app.get("/hurricane_data")
def get_hurricane():
    return hurricanes

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

@app.get("/combined_data")
def get_combined():
    return {"Flood": floods, "Fire": fires, "Hurricane": hurricanes}

@app.get("/{state}/{disaster}")
def return_list(state: str, disaster: str):
    return disaster_list(state, disaster)

@app.get("/mortgages/{state}/{date}")
def return_graph_data(state: str, date: str):
    return mortgage_data_for_state(state, date)

@app.get("/kruskal/{state}/{date}")
def return_kruskal_results(state: str, date: str):
    return kruskal_wallis(state, date)

@app.get("/foreclosures/{state}/{date}")
def return_foreclosure(state: str, date: str):
    return foreclosure_for_state(state, date)
