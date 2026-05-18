import sqlite3 as sql
import os
from pathlib import Path

userDocPath = Path.home() / "Documents" / "FarmMan"
dbFile = "farmman.db"
fullFilePath = os.path.join(userDocPath, dbFile)

class Database():
    def __init__(self):
        super().__init__()

        conn = sql.connect(str(fullFilePath))
        cursor = conn.cursor()

        cursor.execute("""
                        CREATE TABLE IF NOT EXISTS fields(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        crop TEXT,
                        status TEXT,
                        area REAL,
                        geometry TEXT
                        )
                        """)

        conn.commit()
        conn.close()

    def AddFieldDB(name, crop, status, area, geometry):
        conn = sql.connect(str(fullFilePath))
        cursor = conn.cursor()
        cursor.execute("""
                        INSERT INTO fields (name, crop, status, area, geometry)
                        VALUES (?, ?, ?, ?, ?)
                        """, (name, crop, status, area, geometry))
        
        conn.commit()
        conn.close()

    def FetchFields():
        conn = sql.connect(str(fullFilePath))
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, crop, status, area, geometry FROM fields")
        rows = cursor.fetchall()
        conn.close
        return rows
    
    def FetchInField(fieldName):
        conn = sql.connect(str(fullFilePath))
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM fields WHERE name = '{fieldName}'")
        rows = cursor.fetchall()
        conn.close
        return rows

