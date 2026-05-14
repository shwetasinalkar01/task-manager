from flask import Flask, render_template, request, redirect, session
import pymysql
import os

app = Flask(__name__)
app.secret_key = "secretkey"


# ----------------------------
# DB CONNECTION
# ----------------------------
def get_db():
    return pymysql.connect(
        host=os.getenv("MYSQLHOST"),
        user=os.getenv("MYSQLUSER"),
        password=os.getenv("MYSQLPASSWORD"),
        database=os.getenv("MYSQLDATABASE"),
        port=int(os.getenv("MYSQLPORT", 3306)),
        cursorclass=pymysql.cursors.Cursor,
        autocommit=True,
        connect_timeout=5,
        ssl=None
    )


# ----------------------------
# AUTO INITIALIZE DB (SAFE)
# ----------------------------
def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        full_name VARCHAR(255),
        username VARCHAR(255),
        email VARCHAR(255),
        phone VARCHAR(50),
        gender VARCHAR(50),
        department VARCHAR(100),
        address TEXT,
        password VARCHAR(255),
        role VARCHAR(50)
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id INT AUTO_INCREMENT PRIMARY KEY,
        project_name VARCHAR(255),
        description TEXT,
        deadline DATE,
        status VARCHAR(50)
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INT AUTO_INCREMENT PRIMARY KEY,
        task_name VARCHAR(255),
        assigned_to INT,
        project_id INT,
        priority VARCHAR(50),
        status VARCHAR(50),
        start_date DATE,
        end_date DATE
    )
    """)

    conn.close()


# Run once on startup
init_db()


# ----------------------------
# HOME
# ----------------------------
@app.route('/')
def home():
    return redirect('/login')


# ----------------------------
# SIGNUP
# ----------------------------
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        try:
            conn = get_db()
            cur = conn.cursor()

            cur.execute("""
                INSERT INTO users 
                (full_name, username, email, phone, gender, department, address, password, role)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                request.form['full_name'],
                request.form['username'],
                request.form['email'],
                request.form['phone'],
                request.form.get('gender'),
                request.form.get('department'),
                request.form.get('address'),
                request.form['password'],
                request.form['role']
            ))

            conn.close()
            return redirect('/login')

        except Exception as e:
            return f"Signup Error: {str(e)}"

    return render_template('signup.html')


# ----------------------------
# LOGIN
# ----------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            conn = get_db()
            cur = conn.cursor()

            cur.execute("""
                SELECT * FROM users
                WHERE username=%s AND password=%s
            """, (
                request.form['username'].strip(),
                request.form['password'].strip()
            ))

            user = cur.fetchone()
            conn.close()

            if user:
                session['user_id'] = user[0]
                session['name'] = user[1]
                session['username'] = user[2]
                session['role'] = user[9]

                return redirect('/dashboard')
            else:
                return "Invalid username or password"

        except Exception as e:
            return f"Login Error: {str(e)}"

    return render_template('login.html')


# ----------------------------
# DASHBOARD
# ----------------------------
@app.route('/dashboard')
def dashboard():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM users")
    total_users = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM projects")
    total_projects = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM tasks")
    total_tasks = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM tasks WHERE status='Completed'")
    completed_tasks = cur.fetchone()[0]

    conn.close()

    return render_template(
        'dashboard.html',
        total_users=total_users,
        total_projects=total_projects,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks
    )


# ----------------------------
# PROJECTS
# ----------------------------
@app.route('/projects', methods=['GET', 'POST'])
def projects():
    conn = get_db()
    cur = conn.cursor()

    if request.method == 'POST':
        cur.execute("""
            INSERT INTO projects (project_name, description, deadline)
            VALUES (%s,%s,%s)
        """, (
            request.form['project_name'],
            request.form['description'],
            request.form['deadline']
        ))

    cur.execute("SELECT * FROM projects")
    data = cur.fetchall()

    conn.close()
    return render_template('projects.html', projects=data)


# ----------------------------
# TASKS
# ----------------------------
@app.route('/tasks', methods=['GET', 'POST'])
def tasks():
    conn = get_db()
    cur = conn.cursor()

    if request.method == 'POST':
        cur.execute("""
            INSERT INTO tasks 
            (task_name, assigned_to, project_id, priority, status)
            VALUES (%s,%s,%s,%s,%s)
        """, (
            request.form['task_name'],
            request.form['assigned_to'],
            request.form['project_id'],
            request.form['priority'],
            request.form['status']
        ))

    cur.execute("""
        SELECT tasks.id, tasks.task_name, users.full_name,
               projects.project_name, tasks.priority, tasks.status
        FROM tasks
        JOIN users ON tasks.assigned_to = users.id
        JOIN projects ON tasks.project_id = projects.id
    """)
    tasks_data = cur.fetchall()

    cur.execute("SELECT * FROM users")
    users = cur.fetchall()

    cur.execute("SELECT * FROM projects")
    projects = cur.fetchall()

    conn.close()

    return render_template(
        'tasks.html',
        tasks=tasks_data,
        users=users,
        projects=projects
    )


# ----------------------------
# LOGOUT
# ----------------------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


# ----------------------------
# RUN
# ----------------------------
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))