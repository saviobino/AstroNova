import mysql.connector
import json

# Connect to MySQL database
mydb = mysql.connector.connect(
    host="localhost",     # MySQL host
    user="root",          # MySQL username
    password="password",  # MySQL password
    database="baby_names" # Database name
)

mycursor = mydb.cursor()

# Assuming dataid_names_dict is already defined and contains the relevant data
jsondata = json.dumps(dataid_names_dict, indent=4)
data = json.loads(jsondata)

# Loop through the items in the JSON data
for dataid, details in data.items():
    # Prepare the data for insertion
    name_details = json.dumps(details[0], indent=4)
    names_with_similar_meaning = json.dumps(details[1], indent=4)
    numerology_details = json.dumps(details[2], indent=4)
    astrology_details = json.dumps(details[3], indent=4)
    personality_details = json.dumps(details[4], indent=4)

    # SQL query to insert data into the 'details' table
    query = """
    INSERT INTO details (dataid, name_details, names_with_similar_meanings, numerology_details, astrology_details, personality_details)
    VALUES (%s, %s, %s, %s, %s, %s)
    """

    # Values to be inserted into the table
    values = (dataid, name_details, names_with_similar_meaning, numerology_details, astrology_details, personality_details)

    # Execute the query
    mycursor.execute(query, values)

# Commit the transaction
mydb.commit()

# Close the cursor and connection
mycursor.close()
mydb.close()
