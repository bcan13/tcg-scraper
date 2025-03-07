import sqlite3
import datetime
import os
import pandas as pd

def connect_db():

    db_path = os.path.join('core', 'database', 'companies.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # create companies_seen table for all companies we've encountered
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS companies_seen(
            company_name TEXT PRIMARY KEY,
            website TEXT,
            description TEXT,
            job_type TEXT,
            size TEXT,
            location TEXT,
            date_seen DATE
        )
    """)

    # Create companies_sent table for companies we've emailed
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS companies_sent(
            contactee_name TEXT,
            status TEXT,
            company_name TEXT PRIMARY KEY,
            website TEXT,
            description TEXT,
            job_type TEXT,
            size TEXT,
            location TEXT,
            contact_name TEXT,
            email TEXT,
            date_sent DATE
        )
    """)

    conn.commit()

    return conn, cursor

def add_company_seen(company_name, description, job_type, size, location, website):
    conn, cursor = connect_db()
    date_seen = datetime.datetime.now().strftime("%Y-%m-%d")

    cursor.execute("""
        INSERT OR IGNORE INTO companies_seen 
        (company_name, description, job_type, size, location, website, date_seen)
        VALUES (?,?,?,?,?,?,?)
    """, (company_name, description, job_type, size, location, website, date_seen))
    
    conn.commit()
    conn.close()

def add_company_sent(contactee_name, status, company_name, description, job_type, 
                    size, location, website, contact_name, email):
    conn, cursor = connect_db()
    date_sent = datetime.datetime.now().strftime("%Y-%m-%d")

    cursor.execute("""
        INSERT OR IGNORE INTO companies_sent 
        (contactee_name, status, company_name, description, job_type, size, 
         location, website, contact_name, email, date_sent)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
    """, (contactee_name, status, company_name, description, job_type, size, 
          location, website, contact_name, email, date_sent))
    
    conn.commit()
    conn.close()

def company_seen_before(company_name):
    conn, cursor = connect_db()

    cursor.execute("""
        SELECT * FROM companies_seen WHERE company_name = ?
        UNION
        SELECT company_name, description, job_type, size, location, website, date_sent 
        FROM companies_sent WHERE company_name = ?
    """, (company_name, company_name))

    result = cursor.fetchone()
    conn.close()

    return result is not None
# connect_db()
# df = pd.read_csv(os.path.join('..', '..', 'wellfound_output.csv'))
# for index, row in df.iterrows():
#     add_company(contactee_name = "John Doe", status = "Pending", company_name = row['company_name'], description = row['description'], job_type = row['job_type'], size = row['size'], location = row['location'], website = row['website'], email = row['email'])