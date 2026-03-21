from flask import session 
from datetime import date, timedelta

from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)
app.secret_key = 'secret123'

def connect_db():
    return sqlite3.connect("database.db")

def get_weak_topic():
    user_id = session['user_id']
    conn = connect_db()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT topics.name, 
               COUNT(DISTINCT problems.id) as total,
               COUNT(progress.id) as solved
        FROM topics
        LEFT JOIN problems ON topics.id = problems.topic_id
        LEFT JOIN progress ON problems.id = progress.problem_id
        AND progress.user_id = ?
        GROUP BY topics.name
    """, (user_id,))

    data = cur.fetchall()
    conn.close()

    print("AI DATA:", data)

    if not data:
        return "No topics available"

    # 🔥 Case 1: All topics completed
    if all(x[1] == x[2] for x in data):
        return "🎉 All topics completed!"

    # 🔥 Case 2: Nothing started
    if all(x[2] == 0 for x in data):
        return "Start with " + data[0][0]

    # 🔥 Case 3: Find weakest (least progress %)
    weakest = min(data, key=lambda x: (x[2] / x[1]) if x[1] > 0 else 1)

    return "Focus on " + weakest[0]

# 🏠 Home page (form)
@app.route('/')
def home():
    return render_template("index.html")

# ➕ Add problem
@app.route('/add', methods=['POST'])
def add_problem():
    name = request.form['problem']
    topic = request.form['topic']
    difficulty = request.form['difficulty']

    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO problems (problem_name, topic, difficulty)
        VALUES (?, ?, ?)
    """, (name, topic, difficulty))

    conn.commit()
    conn.close()

    return redirect('/dashboard')

# 📊 Dashboard
@app.route('/dashboard')

def dashboard():
    if 'user_id' not in session:
        
        return redirect('/login')

    user_id = session['user_id']
    conn = connect_db()
    cur = conn.cursor()

    # Get all topics
    cur.execute("SELECT id, name FROM topics ORDER BY order_index")
    topics = cur.fetchall()

    topic_data = []
    previous_completed = True 

    for t in topics:
        topic_id = t[0]
        topic_name = t[1]

        cur.execute("""
            SELECT problems.id, problems.problem_name,
            CASE WHEN progress.id IS NOT NULL THEN 1 ELSE 0 END as done
            FROM problems
            LEFT JOIN progress ON problems.id = progress.problem_id
            AND progress.user_id = ?
            WHERE problems.topic_id = ?
        """, (user_id, topic_id,))

        problems = cur.fetchall()

        total = len(problems)
        solved = sum(p[2] for p in problems)

        progress_percent = int((solved / total) * 100) if total > 0 else 0
        # 🔒 Lock logic
        is_unlocked = previous_completed
        previous_completed = (progress_percent == 100)

        topic_data.append({
            "name": topic_name,
            "problems": problems,
            "progress": progress_percent,
            "unlocked": is_unlocked
        })
    cur.execute("SELECT * FROM topics")
    print("TOPICS:", cur.fetchall())

    cur.execute("SELECT * FROM problems")
    print("PROBLEMS:", cur.fetchall())
    cur.execute("SELECT streak FROM users WHERE id=?", (user_id,))
    streak = cur.fetchone()[0]
    conn.close()

    weak_topic = get_weak_topic()
    print("WEAK TOPIC:", weak_topic)
    topic_names = []
    topic_progress = []

    for t in topic_data:
        topic_names.append(t["name"])
        topic_progress.append(t["progress"])
        print("NAMES:", topic_names)
        print("PROGRESS:", topic_progress)
    return render_template("dashboard.html",
                           topics=topic_data,
                           weak=weak_topic,
                           streak = streak,
                           topic_names= topic_names,
                           topic_progress= topic_progress
                        )
    

# mark done 
@app.route('/mark/<int:id>')
def mark_done(id):
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']
    conn = connect_db()
    cur = conn.cursor()

    # Check if already marked
    cur.execute("SELECT * FROM progress WHERE problem_id=? AND user_id=?", (id, user_id))
    existing = cur.fetchone()

    if existing:
        # ❌ UNMARK
        cur.execute("DELETE FROM progress WHERE problem_id=? AND user_id=?", (id, user_id))

    else:
        # ✅ MARK DONE
        cur.execute(
            "INSERT INTO progress (user_id, problem_id, status) VALUES (?, ?, 'done')",
            (user_id, id)
        )

        # 🔥 STREAK LOGIC STARTS HERE
        cur.execute("SELECT streak, last_solved_date FROM users WHERE id=?", (user_id,))
        data = cur.fetchone()

        current_streak = data[0] if data[0] else 0
        last_date = data[1]

        today = date.today()

        if last_date:
            last_date = date.fromisoformat(last_date)
        else:
            last_date = None

        if last_date == today:
            pass  # already counted today
        elif last_date == today - timedelta(days=1):
            current_streak += 1
        else:
            current_streak = 1

        cur.execute("""
            UPDATE users 
            SET streak=?, last_solved_date=? 
            WHERE id=?
        """, (current_streak, today.isoformat(), user_id))

    conn.commit()
    conn.close()

    return redirect('/dashboard')


# SIGN UP ROUTE 
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = connect_db()
        cur = conn.cursor()

        try:
            cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
        except:
            return "User already exists"

        conn.close()
        return redirect('/login')

    return render_template("signup.html")

# login route 
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = connect_db()
        cur = conn.cursor()

        cur.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cur.fetchone()

        conn.close()

        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            return redirect('/dashboard')
        else:
            return "Invalid credentials"
    
    
    return render_template("login.html")

#log out 
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == "__main__":
    app.run(debug=True)