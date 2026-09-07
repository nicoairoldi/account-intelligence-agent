"""
Inital table execution for Neon postgres instance
"""

from database.connection import conn

f = open("database/schema.sql")
sql = f.read()
f.close()

cur = conn.cursor()
cur.execute(sql)
conn.commit()