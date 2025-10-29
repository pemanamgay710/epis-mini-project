import mysql.connector
import streamlit as st

def get_connection():
    """Connect to MySQL Database"""
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="user@123",
            database="final_epis_db"
        )
        return conn
    except mysql.connector.Error as e:
        st.error(f"❌ Database connection failed: {e}")
        return None
