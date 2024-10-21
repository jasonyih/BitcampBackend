import sqlite3
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
from scipy.stats import kruskal
from state_codes import state_codes

# Getting the disaster count for every state using SQL query
def get_disaster_count_per_state():
    # Connecting to our database
    con = sqlite3.connect("disasters.db")
    cur = con.cursor()
    data = {}
    for row in cur.execute("select state, incidentType,  count(*) as count from disasters where incidentType in ('Flood', 'Hurricane', 'Fire') group by state, incidentType"):
        state = row[0]
        incidentType = row[1]
        count = row[2]
        if incidentType not in data:
            data[incidentType] = {state: count}
        elif state not in data[incidentType]:
            data[incidentType][state] = count
        else:
            data[incidentType][state] = count
            
    return data

# Saving the disaster counts as global variables for easy retrieval when called
disaster_count = get_disaster_count_per_state()
fires = disaster_count["Fire"]
floods = disaster_count["Flood"]
hurricanes = disaster_count["Hurricane"]

# Get the disaster list for a certain state or disaster using SQL query
def disaster_list(state, disaster):
    dis_list = {"list": []}
    # Connecting to our database
    con = sqlite3.connect("disasters.db")
    cur = con.cursor()
    join_hurricanes = f"""
        SELECT state, declarationDate, incidentType, declarationTitle, windspeed
        FROM disasters as d LEFT OUTER JOIN hurricanes as h on (d.declarationTitle = h.name)
        WHERE state = '{state}' AND declarationDate > '2008/01/01' AND incidentType = '{disaster}'
        GROUP BY declarationTitle;
    """
    
    #for row in cur.execute(f"select * from disasters where state = '{state}' and declarationDate > '2008/01/01' and incidentType = '{disaster}'"):
    for row in cur.execute(join_hurricanes):
        state = row[0]
        date = row[1]
        incidentType =  row[2]
        declarationTitle = row[3]
        windspeed = row[4]
        # result = cur.execute(f"select windspeed from hurricanes where name = '{str(declarationTitle).split()[1].title()}'")
        # print (result)
        # if incidentType == 'Hurricane':
        #     print(str(declarationTitle).split()[1].title())
        #     windspeed = cur.execute(f"select windspeed from hurricanes where name = '{str(declarationTitle).split()[1].title()}';")
        #     print(windspeed)
        #     dis_list["list"].append({"state": state, "incidentType": incidentType, "date": date, "incidentName": declarationTitle, 'windspeed': windspeed})

        # else:
        dis_list["list"].append({"state": state, "incidentType": incidentType, "date": date, "incidentName": declarationTitle, 'windspeed': windspeed })
    
    return dis_list

# Use SQL query to return all of the mortgage delinquency rate data for a certain state and time stamp
def mortgage_data_for_state(state, date):
    con = sqlite3.connect('disasters.db')
    cur = con.cursor()
    
    date_t = datetime.strptime(date, "%Y-%m")
    begin_date = date_t.replace(year=date_t.year - 1).strftime("%Y-%m")
    end_date = date_t.replace(year=date_t.year + 1).strftime("%Y-%m")
    
    # This setup is for the graph on the frontend
    data = [
        ["Date", state_codes[state], {'type': 'string', 'role': 'style'}]
    ]
    
    query_state = f"""
        SELECT * FROM mortgages 
        WHERE State = '{state_codes[state]}' and Month >= '{begin_date}' and Month <= '{end_date}';
    """
    
    # Going through the query and adding them into the data for the graph
    for (state, rate, month) in cur.execute(query_state):
        # Have to had none for how the graph works
        data.append([month, rate, None])

    return json.dumps(data)

# Performs kruskal-wallis statistical test to determine differences between two groups
def kruskal_wallis(state, date):
    con = sqlite3.connect('disasters.db')
    cur = con.cursor()
    
    date_t = datetime.strptime(date, "%Y-%m")
    # Measuring delinquency rates a year before and then a year after the disaster
    begin_date = date_t.replace(year=date_t.year - 1).strftime("%Y-%m")
    end_date = date_t.replace(year=date_t.year + 1).strftime("%Y-%m")
    
    query_before = f"""
        SELECT Rate FROM mortgages 
        WHERE State = '{state_codes[state]}' and Month >= '{begin_date}' and Month <= '{date}';
    """
    query_after = f"""
        SELECT Rate FROM mortgages 
        WHERE State = '{state_codes[state]}' and Month >= '{date}' and Month <= '{end_date}';
    """

    data_before = []
    
    for (data_point,) in cur.execute(query_before):
        data_before.append(data_point)
    
    data_after = []
    
    for (data_point,) in cur.execute(query_after):
        data_after.append(data_point)
    
    results = kruskal(data_before, data_after)
    return results

# Returns the number of foreclosures for a city around a certain date
def foreclosure_for_state(city, date):
    con = sqlite3.connect('disasters.db')
    cur = con.cursor()
    
    date_t = datetime.strptime(date, "%Y-%m")
    begin_date = date_t.replace(year=date_t.year - 1).strftime("%Y-%m")
    end_date = date_t.replace(year=date_t.year + 1).strftime("%Y-%m")  
    
    # This query will return the counts of foreclosure for each month sorted by month
    query = f"""
        SELECT City, Date, Count(*) as count FROM foreclosures 
        WHERE 
        City = 'atlanta' AND Date >= "{begin_date}" AND  Date <= "{end_date}"
        GROUP BY Date ORDER BY Date ASC;
    """
    
    data = [["Date", city]]
    for (city, date, count) in cur.execute(query):
        data.append([date, count ])
    return json.dumps(data)

app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5175",
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
