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
    password TEXT,
    streak INTEGER DEFAULT 0,
    last_solved_date TEXT
)
""")

# 🔥 Insert topics
topics = [
    ("Arrays", 1),
    ("Strings", 2),
    ("Recursion", 3),
    ("Backtracking", 4),
    ("Linked List", 5),
    ("Stack & Queue", 6),
    ("Trees", 7),
    ("Graphs", 8),
    ("Greedy", 9),
    ("Dynamic Programming", 10)
]

cur.executemany("INSERT INTO topics (name, order_index) VALUES (?, ?)", topics)

# 🔥 Insert problems
problems = [
    (1, "Two Sum", "Easy"),
    (1, "Best Time to Buy Stock", "Easy"),
    (1, "Kadane's Algorithm", "Medium"),

    (2, "Valid Palindrome", "Easy"),
    (2, "Longest Substring Without Repeating", "Medium"),

    (7, "Binary Tree Inorder Traversal", "Easy"),
    (7, "Diameter of Binary Tree", "Medium"),

    (10, "0/1 Knapsack", "Hard"),
    (10, "Longest Increasing Subsequence", "Medium")
]

cur.executemany("INSERT INTO problems (topic_id, problem_name, difficulty) VALUES (?, ?, ?)", problems)

conn.commit()
conn.close()

print("Database created with sample data!")