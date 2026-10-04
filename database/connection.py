"""
Connecting to Neon postgresql instance
"""
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()
connection_string = os.environ["DATABASE_URL"]

conn = psycopg2.connect(connection_string)
