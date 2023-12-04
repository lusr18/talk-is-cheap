'''
TItle: Create DB Script
Author: 
Description: Script to create a SQlite3 database based on a SQL script
'''

import os
import sys
import argparse
import sqlite3

def get_args():
    parser = argparse.ArgumentParser(description="Create a SQLite3 database from a SQL script")
    parser.add_argument("--sql_script", type=str, help="Path to SQL script")
    parser.add_argument("--database_path", type=str, help="Path to SQLite3 database")
    args = parser.parse_args()
    return args


def create_db(args):
    # Check if database file already exists
    if os.path.exists(args.database_path):
        return "Database already exists"
    
    # Create a sqlite3 db
    conn = None
    try:
        conn = sqlite3.connect(args.database_path)
    except sqlite3.Error as e:
        return e

    # Read and execute the sql file
    sql_file = open(args.sql_script)
    try:
        sql_script = sql_file.read()
        cursor = conn.cursor()
        cursor.executescript(sql_script)
        conn.commit()
    except sqlite3.Error as e:
        return e
    finally:
        if conn:
            conn.close()
            
    return "Database created"
            
if __name__ == "__main__":
    args = get_args()
    response = create_db(args)
    print("Create db response: ", response)