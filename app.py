from flask import Flask, render_template, request, redirect, session
import pymysql
import os

app = Flask(__name__)
app.secret_key = "secretkey"

# DB CONNECTION FUNCTION (PURE PYMYSQL)
def get_db():
    return pymysql.connect(
        host=os.getenv("MYSQLHOST"),
        user=os.getenv("MYSQLUSER"),
        password=os.getenv("MYSQLPASSWORD"),
        database=os.getenv("MYSQLDATABASE"),
        port=int(os.getenv("MYSQLPORT", 3306)),
        cursorclass=pymysql.cursors.Cursor
    )

# HOME
@app.route('/')
def home():
    return redirect('/login')


# SIGNUP
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':

        full_name = request.form['full_name']
        username = request.form['username']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        role = request.form['role']

        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO users (full_name, username, email, phone, password, role)
            VALUES (%s,%s,%s,%s,%s,%s)
        """, (full_name, username, email, phone, password, role))

        conn.commit()
        conn.close()

        return redirect('/login')

    return render_template('signup.html')


# LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
            SELECT * FROM users
            WHERE username=%s AND password=%s
        """, (username, password))

        user = cur.fetchone()
        conn.close()

        if user:
            session['user_id'] = user[0]
            session['name'] = user[1]
            session['username'] = user[2]
            session['role'] = user[6]

            return redirect('/dashboard')

    return render_template('login.html')


# DASHBOARD
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


# PROJECTS
@app.route('/projects', methods=['GET', 'POST'])
def projects():

    conn = get_db()
    cur = conn.cursor()

    if request.method == 'POST':

        project_name = request.form['project_name']
        description = request.form['description']
        deadline = request.form['deadline']

        cur.execute("""
            INSERT INTO projects (project_name, description, deadline)
            VALUES (%s,%s,%s)
        """, (project_name, description, deadline))

        conn.commit()

    cur.execute("SELECT * FROM projects")
    data = cur.fetchall()

    conn.close()

    return render_template('projects.html', projects=data)


# TASKS
@app.route('/tasks', methods=['GET', 'POST'])
def tasks():

    conn = get_db()
    cur = conn.cursor()

    if request.method == 'POST':

        task_name = request.form['task_name']
        assigned_to = request.form['assigned_to']
        project_id = request.form['project_id']
        priority = request.form['priority']
        status = request.form['status']

        cur.execute("""
            INSERT INTO tasks (task_name, assigned_to, project_id, priority, status)
            VALUES (%s,%s,%s,%s,%s)
        """, (task_name, assigned_to, project_id, priority, status))

        conn.commit()

    cur.execute("""
        SELECT tasks.id, tasks.task_name, users.full_name,
               projects.project_name, tasks.priority, tasks.status
        FROM tasks
        JOIN users ON tasks.assigned_to = users.id
        JOIN projects ON tasks.project_id = projects.id
    """)

    tasks = cur.fetchall()

    cur.execute("SELECT * FROM users")
    users = cur.fetchall()

    cur.execute("SELECT * FROM projects")
    projects = cur.fetchall()

    conn.close()

    return render_template(
        'tasks.html',
        tasks=tasks,
        users=users,
        projects=projects
    )


# LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))