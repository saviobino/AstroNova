import streamlit as st
import mysql.connector
import pandas as pd
import requests
from bs4 import BeautifulSoup
import json

# --- Database Connection ---
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="password",
        database="baby_names"
    )

# --- Data Scraping Functions ---
def clean_gender(gender):
    gender = gender.strip().title()
    return gender if gender in ['Boy', 'Girl'] else 'Unknown'

def scrape_page(page_url):
    page = requests.get(page_url)
    soup = BeautifulSoup(page.text, "html.parser")
    table = soup.find('table', class_="table name-list-wrapper bordered")
    if not table:
        return pd.DataFrame()
    headers = [th.text.strip() for th in table.find_all('th')] + ["DataID"]
    df = pd.DataFrame(columns=headers)
    for row in table.find_all('tr')[1:]:
        row_data = [td.text.strip() for td in row.find_all('td')]
        data_id = row.get('data-id')
        if len(row_data) == len(headers) - 1:
            row_data.append(data_id)
            df.loc[len(df)] = row_data
    return df

def scrape_basic():
    base_url = "https://www.prokerala.com/kids/baby-names/?religion=&origin=&baby_name_meaning=&process=2&page="
    conn = get_connection()
    cursor = conn.cursor()
    page_number = 1
    while True:
        df = scrape_page(base_url + str(page_number))
        if df.empty:
            break
        for _, row in df.iterrows():
            gender = clean_gender(row['Gender'])
            sql = """
            INSERT IGNORE INTO names (dataid, name, meaning, gender, religion)
            VALUES (%s, %s, %s, %s, %s)
            """
            vals = (int(row['DataID']), row['Name'], row['Meaning'], gender, row['Religion'])
            cursor.execute(sql, vals)
        conn.commit()
        page_number += 1
    cursor.close()
    conn.close()
    st.success("Basic name data scraped successfully!")

def scrape_details():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, dataid FROM names")
    rows = cursor.fetchall()
    baseurl = "https://www.prokerala.com/kids/baby-names/"
    for name, dataid in rows:
        formatted = name.replace("'", "-").lower()
        url = f"{baseurl}{formatted}-{dataid}.html"
        response = requests.get(url)
        if response.status_code != 200:
            continue
        soup = BeautifulSoup(response.text, 'html.parser')
        p_tag = soup.find_all('p')
        similar = []
        if len(p_tag) >= 3:
            for i in p_tag:
                a_tags = i.find_all('a')
                out = [a.get_text(strip=True) for a in a_tags]
                similar.append(out)
        tables = soup.find_all('table', class_="table")
        numerology = [i.get_text(strip=True) for i in soup.find('div', {'class': 'name-details-wrapper item-block shadow'}).find_all('td')] if soup.find('div', {'class': 'name-details-wrapper item-block shadow'}) else []
        name_details = [i.get_text(strip=True) for i in tables[0].find_all('td')] if len(tables) > 0 else []
        astrology = [i.get_text(strip=True) for i in soup.find('table', class_='table shadow').find_all('td')] if soup.find('table', class_='table shadow') else []
        personality = []
        p_tables = soup.find_all('table', class_="table table-striped shadow")
        if len(p_tables) > 1:
            personality = [i.get_text(strip=True) for i in p_tables[1].find_all('td')]
        query = """
        INSERT INTO details (dataid, name_details, names_with_similar_meanings, numerology_details, astrology_details, personality_details)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        vals = (
            dataid,
            json.dumps(name_details),
            json.dumps(similar),
            json.dumps(numerology),
            json.dumps(astrology),
            json.dumps(personality)
        )
        try:
            cursor.execute(query, vals)
            conn.commit()
        except:
            conn.rollback()
    cursor.close()
    conn.close()
    st.success("Detailed name data scraped successfully!")

# --- UI ---
st.title("🌸 Baby Names Data Scraper & Viewer")

option = st.sidebar.selectbox(
    "Select an action",
    ["View Database", "Scrape Basic Data", "Scrape Detailed Data"]
)

if option == "Scrape Basic Data":
    if st.button("Start Scraping"):
        scrape_basic()

elif option == "Scrape Detailed Data":
    if st.button("Scrape Details"):
        scrape_details()

else:
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM names", conn)
    conn.close()
    st.dataframe(df)
    st.info(f"{len(df)} names currently in database.")
