# Vlado Situm
# CNA 330 Fall quarter 2020
# Date Nov 10, 2020
# This script pulls jobs positions from API https://jobs.github.com/positions.json
# Configuration file Param1.JSON is used for Pycharm configuration.
# and stores them into database "job_hunters" on the WAMP Server.
# If there is a new posting it notifies the user. I wrote this code together with my classmates
# Dorin, Igor, Abdi and tutor Liviu Patrasco who helped us the most. Also I used teacher Justin's code example
# "fantasyfootball" which was my backbone to write Jobhunter.py.


import mysql.connector
import sys
import json
import urllib.request
import os
import time
from datetime import datetime


# Connect to database
# You may need to edit the connect function based on your local settings.
def connect_to_sql():
    config = {
        'user': 'root',
        'password': '',
        'host': 'localhost',
        'port': '3306',
        'database': 'job_hunters'
    }
    conn = mysql.connector.connect(**config)
    return conn


# Create the table structure
def create_tables(cursor, table):
    ## Add your code here. Starter code below
    sql = 'CREATE TABLE IF NOT EXISTS jobs (id INT PRIMARY KEY AUTO_INCREMENT, type VARCHAR(100), ' \
          'title VARCHAR(100), description TEXT, job_id VARCHAR(50), created_at DATETIME, company VARCHAR(100), ' \
          'location VARCHAR(100), how_to_apply text) CHARACTER SET utf8mb4; '

    query_sql(cursor, sql)


# Query the database.
# You should not need to edit anything in this function
def query_sql(cursor, query):
    cursor.execute(query)
    return cursor


# Add a new job
def add_new_job(cursor, jobdetails):
    ## Add your code here
    date_format = '%a %b %d %H:%M:%S UTC %Y'
    query = '''INSERT INTO jobs (type, title, description, job_id, created_at, company, location, how_to_apply) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s);'''

    cursor.execute('SET NAMES utf8mb4;')

    if jobdetails['id'] == '46ab84b4-12dc-4a95-ab08-422428554dfc':
        print(jobdetails)


    cursor.execute(query, (
        jobdetails['type'],
        jobdetails['title'],
        jobdetails['description'],
        jobdetails['id'],
        datetime.strptime(jobdetails['created_at'], date_format),
        jobdetails['company'],
        jobdetails['location'],
        jobdetails['how_to_apply']))

    return


# Check if new job
def check_if_job_exists(cursor, jobdetails):
    ## Add your code here
    query = "SELECT COUNT(*) FROM jobs where job_id = '{}';".format(jobdetails['id'])

    return query_sql(cursor, query)


def delete_job(cursor, jobdetails):
    ## Add your code here
    query_sql(cursor, 'delete from jobs where created_at < DATE_SUB(NOW(), INTERVAL 30 DAY);')


# Grab new jobs from a website
def fetch_new_jobs(arg_dict):
    # Code from https://github.com/RTCedu/CNA336/blob/master/Spring2018/Sql.py
    query = "https://jobs.github.com/positions.json?" + '&'.join(
        '{}={}'.format(key, value) for key, value in arg_dict.items())  # Add arguments here

    jsonpage = 0
    try:
        contents = urllib.request.urlopen(query)
        response = contents.read()
        jsonpage = json.loads(response)
    except:
        pass
    return jsonpage


# Load a text-based configuration file
def load_config_file(filename):
    argument_dictionary = {}
    # Code from https://github.com/RTCedu/CNA336/blob/master/Spring2018/FileIO.py
    rel_path = os.path.abspath(os.path.dirname(__file__))
    file = 0
    file_contents = '{ "title" : "Software", "location" : "Remote" }'
    try:
        file = open(filename, "r")
        file_contents = file.read()
    except FileNotFoundError:
        print("File not found, it will be created.")
        file = open(filename, "w")
        file.write('{ "title" : "Software", "location" : "Remote" }')
        file.close()

    ## Add in information for argument dictionary
    argument_dictionary = json.loads(file_contents)
    return argument_dictionary


# Main area of the code.
def jobhunt(cursor, arg_dict):
    # Fetch jobs from website
    # print(arg_dict)
    jobpage = fetch_new_jobs(arg_dict)

    ## Add your code here to parse the job page

    for jobdetails in jobpage:
        count = check_if_job_exists(cursor, jobdetails).fetchone()

        if count[0] == 0:
            add_new_job(cursor, jobdetails)
            print("Hey user, there is a new job posting! Check this out: " + json.dumps(jobdetails))


    ## Add in your code here to check if the job already exists in the DB

    ## Add in your code here to notify the user of a new posting

    ## EXTRA CREDIT: Add your code to delete old entries
    delete_job(cursor, jobdetails)


# Setup portion of the program. Take arguments and set up the script
# You should not need to edit anything here.
def main():
    # Connect to SQL and get cursor
    conn = connect_to_sql()
    cursor = conn.cursor()
    create_tables(cursor, "jobs")
    # Load text file and store arguments into dictionary
    # { "title" : "Software", "location" : "Remote" }
    arg_dict = load_config_file(sys.argv[1])
    while (1):
        jobhunt(cursor, arg_dict)
        conn.commit()
        time.sleep(3600)  # Sleep for 1h


if __name__ == '__main__':
    main()
