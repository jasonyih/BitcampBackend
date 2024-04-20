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

def get_df_based_on_date(state, begin_date):
    parts = begin_date.split("-")
    begin_date = parts[0] + "-" + parts[1]
    date_t = datetime.strptime(begin_date, "%Y-%m")
    end_date = date_t.replace(year=date_t.year + 1).strftime("%Y-%m")
    new_df = pd.DataFrame()
    row = mortgages[mortgages['Name'] == state]
    for column in row.columns:
        if column >= begin_date and column <= end_date:
            new_df[column] = row[column]
    
    return new_df

def make_graph(data):
    plt.figure(figsize=(10, 6))
    for index, row in data.iterrows():
        plt.plot(row.index, row.values, marker='o', label=index)

    # Customize the plot
    plt.title('Mortgage Delinquency Rates')
    plt.xlabel('Date')
    plt.ylabel('Delinquency Rate')
    plt.xticks(rotation=45)
    plt.legend(title='Index')

    img_bytes = io.BytesIO()
    plt.savefig(img_bytes, format='png', bbox_inches='tight')
    plt.close()
    img_bytes.seek(0)

    return img_bytes

def get_disasters(state, disaster):
    dis_list = {"list": []}
    for index, row in disasters.iterrows():
        if row['incidentBeginDate'] >= "2010" and row['incidentType'] == disaster and row['state'] == state:
            date = row['incidentBeginDate']
            dis_list["list"].append({"state": row['state'], "incidentType": row['incidentType'], "date": date[:date.index("T")]})
    
    return dis_list

# df = get_df_based_on_date("Texas", "2018-09")
# img_bytes = make_graph(df)
# i = Image.open(img_bytes)
# i.show()

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

@app.get("/{state}/{disaster}")
def return_list(state: str, disaster: str):
    return get_disasters(state, disaster)

@app.get("/{state}/{disaster}/{date}")
def return_graph(state: str, disaster: str, date: str):
    df = get_df_based_on_date(state, date)
    img_bytes = make_graph(df)

    return Response(content=img_bytes.getvalue(), media_type="image/png")
