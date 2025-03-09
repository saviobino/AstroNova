import mysql.connector
import pandas as pd
import requests
from bs4 import BeautifulSoup
import json

# SQL Connectivity
mydb = mysql.connector.connect(
    host="localhost",     # MySQL host
    user="root",          # MySQL username
    password="password",  # MySQL password
    database="baby_names" # Database name
)

mycursor = mydb.cursor()

# Function to clean gender data before insertion
def clean_gender(gender):
    # Remove any leading/trailing spaces and convert to title case
    gender = gender.strip().title()
    # Check if the value is valid (assuming 'Boy' or 'Girl' are valid values)
    if gender not in ['Boy', 'Girl']:
        return 'Unknown'  # Default value if the gender is invalid or unknown
    return gender

# Function to insert data_id into the database
def insert_data_id(data_id):
    try:
        if data_id is not None:
            sql = "INSERT IGNORE INTO names (dataid) VALUES (%s)"
            mycursor.execute(sql, (data_id,))
        else:
            print("Skipped inserting None dataid")
        mydb.commit()
    except mysql.connector.Error as err:
        print(f"Error inserting data_id {data_id}: {err}")

# Function to scrape a single page and return a DataFrame
def scrape_page(page_url):
    page = requests.get(page_url)
    soup = BeautifulSoup(page.text, "html.parser")

    # Find the table
    table = soup.find('table', class_="table name-list-wrapper bordered")
    if not table:
        print(f"No table found on page: {page_url}")
        return pd.DataFrame()

    # Extract table headers
    headers = [th.text.strip() for th in table.find_all('th')]
    headers.append("DataID")  # Add DataID to the headers for the extra column

    # Initialize DataFrame with extracted headers
    df = pd.DataFrame(columns=headers)

    # Extract table rows
    rows = table.find_all('tr')[1:]  # Skip the header row

    # Loop through rows and extract data
    for row in rows:
        row_data = row.find_all('td')  # Get all <td> elements
        individual_rowdata = [td.text.strip() for td in row_data]  # Extract text and strip whitespace
        data_id = row.get('data-id')  # Extract the 'data-id' attribute

        # Skip rows where data doesn't match the number of columns
        if len(individual_rowdata) == len(headers) - 1:  # Account for the added DataID
            individual_rowdata.append(data_id)  # Append the DataID to the row
            df.loc[len(df)] = individual_rowdata  # Add row to DataFrame

    return df

# Base URL for scraping
base_url = "https://www.prokerala.com/kids/baby-names/?religion=&origin=&baby_name_meaning=&process=2&page="

# Scrape multiple pages
def scrape():
    page_number = 1
    while True:
        print(f"Scraping page {page_number}...")
        page_url = base_url + str(page_number)
        df = scrape_page(page_url)

        # If no data is returned, break the loop (end of pages)
        if df.empty:
            print("No more data to scrape. Exiting.")
            break

        # Insert data into MySQL
        for index, row in df.iterrows():
            # Insert the data_id first
            if 'DataID' in row and row['DataID']:
                try:
                    data_id = int(row['DataID'])  # Ensure data_id is an integer
                    insert_data_id(data_id)
                except ValueError as ve:
                    print(f"Invalid data_id {row['DataID']}: {ve}")

            # Clean the gender value before inserting
            gender = clean_gender(row['Gender'])

            # Prepare the INSERT INTO statement
            sql = """
            INSERT IGNORE INTO names (dataid, name, meaning, gender, religion)
            VALUES (%s, %s, %s, %s, %s)
            """
            values = (
                int(row['DataID']) if row['DataID'] else None,  # Ensure data_id is an integer
                row['Name'],
                row['Meaning'],
                gender,
                row['Religion']
            )

            try:
                # Execute the query
                mycursor.execute(sql, values)
            except mysql.connector.Error as err:
                print(f"Error inserting data: {err}")

        # Commit the changes to the database
        mydb.commit()

        # Increment the page number
        page_number += 1

    print("All data has been inserted successfully!")

# Fetch name and dataid from the database
def scrape_details():
    query = "SELECT name, dataid FROM names"
    mycursor.execute(query)
    rows = mycursor.fetchall()

    # Create a dictionary to store the results
    dataid_names_dict = {}

    # Base URL for scraping
    baseurl = "https://www.prokerala.com/kids/baby-names/"

    # Loop through the name and dataid pairs
    for name, dataid in rows:
        # Format the name to replace apostrophes with hyphens and make it lowercase
        formatted_name = name.replace("'", "-").lower()
        
        # Construct the URL for the specific name and dataid
        url = f"{baseurl}{formatted_name}-{dataid}.html"
        print(f"Fetching URL: {url}")

        # Send a GET request to the webpage
        response = requests.get(url)
        
        # Check if the page exists
        if response.status_code != 200:
            print(f"Failed to retrieve data for {name}-{dataid}. Status code: {response.status_code}")
            continue
        
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.text, 'html.parser')
        p_tag = soup.find_all('p')
        names_with_similar_meaning = []

        # Check if there are at least 3 <p> tags
        if len(p_tag) >= 3:
            third_p = p_tag[2]  # Access the 3rd <p> tag (index 2)
            for i in p_tag:
                a_tags = i.find_all('a')
                out = [a.get_text(strip=True) for a in a_tags]
                names_with_similar_meaning.append(out)
            
            # Get the first word of the 3rd paragraph
            first_word = third_p.text.strip().split()[0].lower()  # Convert to lowercase for comparison
            if first_word == "below":
                print("The first word of the 3rd <p> tag is 'Below'. Applying specific condition.")
                # Find all <a> tags inside the 3rd <p> tag
                a_tags = third_p.find_all('a')
                out = [a.get_text(strip=True) for a in a_tags]
                names_with_similar_meaning.append(out)

        # Extract the tables with details
        tables = soup.find_all('table', class_="table")
        container = soup.find('div', {'class': 'name-details-wrapper item-block shadow'})
        numerology_table = container.find('table') if container else None
        numerologydetails = [item.get_text(strip=True) for item in numerology_table.find_all('td')] if numerology_table else []

        # Extract name details from table[0]
        name_details = [item.get_text(strip=True) for item in tables[0].find_all('td')] if len(tables) > 0 else []

        # Extract astrology details
        astrology_table = soup.find('table', class_='table shadow')
        astrology_details = [item.get_text(strip=True) for item in astrology_table.find_all('td')] if astrology_table else []

        # Extract personality details
        personality_tables = soup.find_all('table', class_="table table-striped shadow")
        personality_details = [item.get_text(strip=True) for item in personality_tables[1].find_all('td')] if len(personality_tables) > 1 else []

        # Store the collected data in the dictionary
        dataid_names_dict[dataid] = [
            name_details,
            names_with_similar_meaning,
            numerologydetails,
            astrology_details,
            personality_details
        ]
        
        # Insert the data into the details table
        query = """
        INSERT INTO details (dataid, name_details, names_with_similar_meanings, numerology_details, astrology_details, personality_details)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        values = (
            dataid,
            json.dumps(name_details, indent=4),
            json.dumps(names_with_similar_meaning, indent=4),
            json.dumps(numerologydetails, indent=4),
            json.dumps(astrology_details, indent=4),
            json.dumps(personality_details, indent=4)
        )

        try:
            mycursor.execute(query, values)
            mydb.commit()
            print(f"Data successfully inserted for dataid: {dataid}")
        except mysql.connector.Error as err:
            print(f"dataid already exists: {dataid}. Error: {err}")
            mydb.rollback()

# Main execution
if __name__ == "__main__":
    scrape()
    scrape_details()

    # Close the cursor and connection
    mycursor.close()
    mydb.close()

    print("All data has been processed successfully!")
