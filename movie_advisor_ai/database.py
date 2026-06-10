import os
import sqlite3

# Get the absolute path of the directory where database.py is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Construct the dynamic absolute path to the SQLite database file
DB_NAME = os.path.join(BASE_DIR, "movie_cache.db")

def init_db():
    """Initializes all necessary tables in the database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 1. AI Cache Table
    # Uses a unique composite text key for instantaneous lookups of pre-generated descriptions
    cursor.execute('''CREATE TABLE IF NOT EXISTS cache 
                      (key TEXT PRIMARY KEY, description TEXT)''')
    
    # 2. Clients Table
    # Stores primary user profiles used for audience segmentation and targeting
    cursor.execute('''CREATE TABLE IF NOT EXISTS clients 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       email TEXT,
                       age_group TEXT,
                       interest TEXT)''')
    
    # 3. Delivery Queue Table
    # Optimized structure to store and moderate group-based message templates
    cursor.execute('''CREATE TABLE IF NOT EXISTS delivery_queue 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       age_group TEXT,
                       interest TEXT,
                       movie_name TEXT,
                       description TEXT,
                       status TEXT DEFAULT 'pending')''')
    
    # Commit changes (transactions) to the database
    conn.commit()
    # Close the connection to free up system resources
    conn.close()

# --- Client Management Functions ---

def add_client(email, age_group, interest):
    """Adds a new client record to the database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Secure parameterized query to prevent SQL injection vulnerabilities
    cursor.execute("INSERT INTO clients (email, age_group, interest) VALUES (?, ?, ?)", 
                   (email, age_group, interest))
    conn.commit()
    conn.close()

def get_random_clients(limit):
    """Selects a pseudo-random set of clients for delivery."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Fetch random records with a constraint on row count via the LIMIT operator
    cursor.execute("SELECT email, age_group, interest FROM clients ORDER BY RANDOM() LIMIT ?", (limit,))
    rows = cursor.fetchall()  # Extract all matching rows as a list of tuples
    conn.close()
    return rows

# --- Queue Management Functions ---

def save_group_to_queue(age_group, interest, movie, description):
    """Saves a generated group message template into the delivery queue."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Logging template metadata and the generated text with a default 'pending' status
    cursor.execute(
        "INSERT INTO delivery_queue (age_group, interest, movie_name, description) VALUES (?, ?, ?, ?)", 
        (age_group, interest, movie, description)
    )
    conn.commit()
    conn.close()

def get_current_queue():
    """Fetches all un-sent templates with a 'pending' status to display in the UI."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Retrieve un-sent templates filtered by their active readiness state
    cursor.execute("SELECT id, age_group, interest, movie_name, description FROM delivery_queue WHERE status='pending'")
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_cached_recommendation(movie_name, age_group, interest):
    """Searches for an already existing description within the cache table."""
    conn = sqlite3.connect(DB_NAME) 
    cursor = conn.cursor()
    # Form the unique composite string key for fast row lookup
    key = f"{movie_name}_{age_group}_{interest}"
    cursor.execute("SELECT description FROM cache WHERE key=?", (key,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def get_clients_by_group(age_group, interest, limit):
    """Queries the database for clients matching exact targeting criteria."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor() 
    # Precise multi-attribute audience filtering (targeting) executed simultaneously
    cursor.execute(
        "SELECT email, age_group, interest FROM clients WHERE age_group=? AND interest=? ORDER BY RANDOM() LIMIT ?", 
        (age_group, interest, limit)
    )
    rows = cursor.fetchall()
    conn.close()
    return rows

def save_to_cache(movie_name, age_group, interest, description):
    """Saves a newly generated description into the database cache."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Combine parameters to update or insert the payload into cache table securely
    key = f"{movie_name}_{age_group}_{interest}"
    cursor.execute("INSERT OR REPLACE INTO cache VALUES (?, ?)", (key, description))
    conn.commit()
    conn.close()