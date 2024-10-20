from datetime import datetime
import sqlite3
import pandas as pd
import os

create_disaster = False
create_mortgage = False
create_foreclosure = False

if create_disaster: 
    disasters = pd.read_csv("DisasterDeclarationsSummaries.csv")

    con = sqlite3.connect("disasters.db")
    cur = con.cursor()

    data = []
    for index, row in disasters.iterrows():
        incidentType = row['incidentType']
        state = row['state']
        declarationDate = row['declarationDate']
        declarationTitle = row['declarationTitle']
        data.append((state, declarationDate, incidentType, declarationTitle))
        
    cur.executemany("INSERT INTO disasters VALUES(?, ?, ?, ?)", data)
        
    con.commit()

if create_mortgage:
    mortgages = pd.read_csv('StateMortgagesPercent-30-89DaysLate-thru-2023-09.csv')

    con = sqlite3.connect('disasters.db')
    cur = con.cursor()
    
    cur.execute("DROP TABLE mortgages")

    new_table = """
        CREATE TABLE mortgages (
            State VARCHAR(255),
            Rate REAL,
            Month DATE
        ); 
    """
    con.execute(new_table)


    mortgages = pd.read_csv('StateMortgagesPercent-30-89DaysLate-thru-2023-09.csv')

    data = []

    for index, row in mortgages.iterrows():
        state = row['Name']
        for col in mortgages.columns:
            if col != "RegionType" and col != "Name" and col != "FIPSCode":
                data.append((state, row[col], col))

    cur.executemany("INSERT INTO mortgages VALUES(?, ?, ?)", data)
    con.commit()

if create_foreclosure:
    foreclosures = pd.read_csv('atlanta.csv')
    con = sqlite3.connect('disasters.db')
    cur = con.cursor()
    
    cur.execute("DROP TABLE foreclosures")
    
    new_table = """
        CREATE TABLE foreclosures (
            City VARCHAR(255),
            Date DATE
        )
        
    """
    
    cur.execute(new_table)
    
    data = []
    for index, row in foreclosures.iterrows():
        city = 'atlanta'
        date = row['Foreclosure_date']
        
        if not pd.isna(date):
            date_object = datetime.strptime(str(int(date)), '%m%Y')
            # Formatting the date as year-month
            formatted_date = date_object.strftime('%Y-%m')
            data.append((city, formatted_date))
            
    cur.executemany("INSERT INTO foreclosures VALUES (?,?)", data)
    con.commit()
    
conn = sqlite3.connect('disasters.db')

db_size_bytes = os.path.getsize('disasters.db')

conn.close()

print(f"Database size: {db_size_bytes} bytes") 