import requests
from bs4 import BeautifulSoup
import sqlite3

# Connecting to the database
con = sqlite3.connect("disasters.db")
cur = con.cursor()

data = []
# Go through every year since 2008
for year in range(24, 8, -1):

    # URL of the website to scrape (replace with the actual URL)
    url = f"https://products.climate.ncsu.edu/weather/hurricanes/database/?search=year&yr=20{year}"

    # Send a GET request to the website
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the content with BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all rows that contain the hurricane data (adjust the class if necessary)
        hurricane_rows = soup.select('.hurrdb_storms_table_row0, .hurrdb_storms_table_row1')

        for row in hurricane_rows:
            hurricane_name = row.select_one('div:nth-child(2)').get_text(strip=True)
            if hurricane_name != "(unnamed)":
                wind_speed = row.select_one('div:nth-child(4)').get_text(strip=True)
                data.append(("HURRICANE "+ hurricane_name.upper(), int(wind_speed)))
                
            
    else:
        print("Failed to retrieve the webpage")
        
cur.execute("DROP TABLE hurricanes;")

new_table = """
    CREATE TABLE hurricanes (
        name VARCHAR(255),
        windspeed INTEGER
    ); 
"""
con.execute(new_table)

cur.executemany("INSERT INTO hurricanes VALUES(?, ?)", data)
con.commit()