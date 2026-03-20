import sqlite3

conn = sqlite3.connect("database.db")
cur = conn.cursor()

# Create topics table
cur.execute("""
CREATE TABLE IF NOT EXISTS topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    order_index INTEGER
)
""")

# Create problems table
cur.execute("""
CREATE TABLE IF NOT EXISTS problems (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id INTEGER,
    problem_name TEXT,
    difficulty TEXT
)
""")

# Create progress table
cur.execute("""
CREATE TABLE IF NOT EXISTS progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    problem_id INTEGER,
    status TEXT
)
""")

# Users Table 

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")

# 🔥 Insert topics
topics = [
    ("Arrays", 1),
    ("Recursion", 2),
    ("Dynamic Programming", 3)
]

cur.executemany("INSERT INTO topics (name, order_index) VALUES (?, ?)", topics)

# 🔥 Insert problems
problems = [
    (1, "Two Sum", "Easy"),
    (1, "Kadane's Algorithm", "Medium"),
    (2, "Subset Generation", "Medium"),
    (3, "Knapsack", "Hard")
]

cur.executemany("INSERT INTO problems (topic_id, problem_name, difficulty) VALUES (?, ?, ?)", problems)

conn.commit()
conn.close()

print("Database created with sample data!")