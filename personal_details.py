import requests
from bs4 import BeautifulSoup
import json
import mysql.connector

# Connect to the MySQL database
mydb = mysql.connector.connect(
    host="localhost",     # MySQL host
    user="root",          # MySQL username
    password="password",  # MySQL password
    database="baby_names" # Database name
)

dictdata={}

mycursor = mydb.cursor()

# Fetch name and dataid from the database
query = "SELECT name, dataid FROM names"  # replace `your_table_name` with your actual table name
mycursor.execute(query)
rows = mycursor.fetchall()

# Create a dictionary with name as key and dataid as value
name_dataid_dict = {name: dataid for name, dataid in rows}

# Base URL for scraping
baseurl = "https://www.prokerala.com/kids/baby-names/"


# Loop through the name and dataid pairs
for name, dataid in name_dataid_dict.items():
    # Format the name to replace apostrophes with hyphens and make it lowercase
    formatted_name = name.replace("'", "-").lower()
    
    # Construct the URL for the specific name and dataid
    url = f"{baseurl}{formatted_name}-{10}.html"
    
    #SIMILAR NAMES
    # Send a GET request to the webpage
    response = requests.get(url)
    
    # Check if the page exists
    if response.status_code != 200:
        print(f"Failed to retrieve data for {name}-{dataid}. Status code: {response.status_code}")
        continue
    
    # Parse the HTML content of the page
    soup = BeautifulSoup(response.text, 'html.parser')
    
    p_tag = soup.find('p')

    # Extract all <a> tags within the <p> tag
    a_tags = p_tag.find_all('a')

    # Create a list to store only the names (text inside <a>)
    names = [a.get_text(strip=True) for a in a_tags]
    
    
    response = requests.get(url)
    

   
    
    # Check if the page exists
    if response.status_code != 200:
        print(f"Failed to retrieve data for {name}-{dataid}. Status code: {response.status_code}")
        continue
    
    # Parse the HTML content of the page
    soup = BeautifulSoup(response.text, 'html.parser')
    table=soup.find_all('table',class_="table")
    name = table[1]

    # Check if any <td> in table[1] has the text "Numerology Number"
    contains_numerology_number = False
    for row in table[2].find_all('tr'):  # Iterate over rows
        for cell in row.find_all('td'):  # Iterate over cells
            if cell.text.strip() == "Numerology Number":
                contains_numerology_number = True
                break
        if contains_numerology_number:
            break

    # If the condition is met, switch to table[2]
    if contains_numerology_number:
        name = table[2]

    # Process the selected table (name)
    print("Selected table contents:")
    for row in name.find_all('tr'):
        print(row.text.strip())

    
    # Check if the page exists
    if response.status_code != 200:
        print(f"Failed to retrieve data for {name}-{dataid}. Status code: {response.status_code}")
        continue
    
    # Parse the HTML content of the page
    soup = BeautifulSoup(response.text, 'html.parser')
    astrology=soup.find('table',class_='table shadow')
    for i in astrology:
        print(i.text.strip())        
    
    # Check if the page exists
    if response.status_code != 200:
        print(f"Failed to retrieve data for {name}-{dataid}. Status code: {response.status_code}")
        continue
    
    soup = BeautifulSoup(response.text, 'html.parser')
    personality=soup.find_all('table',class_="table table-striped shadow")
    for i in personality[1]:
        print(i.text.strip())
        
    

    

    
    