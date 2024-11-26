import logging
import os
import pyodbc
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS

app = Flask(__name__)

CORS(app)

# Configure logging with method name
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')

# SQL Server connection details from environment variables
server = '34.57.106.211'
database = 'myappdb'
username = 'sqlserver'
password = 'Tn50@4669'

# Connection string
# Updated connection string with connection pooling parameters
conn_str = (
    f'DRIVER={{ODBC Driver 17 for SQL Server}};'
    f'SERVER={server};'
    f'DATABASE={database};'
    f'UID={username};'
    f'PWD={password};'
    f'Timeout=30;'
    f'Pooling=True;'
    f'MinPoolSize=5;'  # Minimum number of connections in the pool
    f'MaxPoolSize=20;'  # Maximum number of connections in the pool
)

def get_connection():
    """Gets a connection from the connection pool."""
    try:
        return pyodbc.connect(conn_str)
    except pyodbc.Error as e:
        logging.error(f"Connection pool error: {e}")
        return None

def check_database_connection():
    """Checks the database connection."""
    try:
        conn = get_connection()
        if conn:
            conn.close()
            return True
    except pyodbc.Error as e:
        logging.error(f"Database connection error: {e}")
    return False

@app.route('/')
def home():
    """Home route that shows database connection status."""
    if check_database_connection():
        message = "Database connection successful, DB up and running."
    else:
        message = "Database connection failed. Please check the configuration."
    return jsonify(message=message)

@app.route('/validate', methods=['POST'])
def validate_login():
    """Validates the login credentials."""
    username = request.json.get('username')
    password = request.json.get('password')

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Query to check if the username and password match
        cursor.execute("SELECT * FROM Login WHERE username = ? AND password = ?", (username, password))
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        return jsonify(valid=(result is not None))

    except pyodbc.Error as e:
        logging.error(f"Database error: {e}")
        return jsonify(error=str(e)), 500

@app.route('/logins', methods=['GET'])
def get_logins():
    """Fetches all login entries from the database."""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Query to get all users from the Login table
        cursor.execute("SELECT username, password FROM Login")  # Select both username and password
        logins = cursor.fetchall()

        cursor.close()
        conn.close()

        # Format the data to return as JSON
        login_list = [{'username': row[0], 'password': row[1]} for row in logins]  # Convert to a list of dicts
        return jsonify(login_list)

    except pyodbc.Error as e:
        logging.error(f"Database error: {e}")
        return jsonify(error=str(e)), 500

@app.route('/connection')
def connection_status():
    """Checks and renders connection status."""
    if check_database_connection():
        message = "Connection successful"
    else:
        message = "Connection failed"

    return render_template('status.html', message=message)

@app.route('/status', methods=['GET'])
def status():
    """Route to check the status of the application."""
    return jsonify({"status": "Application is running"}), 200

if __name__ == '__main__':
    if check_database_connection():
        logging.info("Database connection successful, DB up and running.")
    app.run(host='0.0.0.0', port=5001, debug=True)
