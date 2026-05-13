from flask import Flask, render_template, request, redirect, session
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = "secretkey"

# MYSQL CONFIG
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'shweta@1201'
app.config['MYSQL_DB'] = 'team_manager'

mysql = MySQL(app)

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
        gender = request.form['gender']
        department = request.form['department']
        address = request.form['address']
        password = request.form['password']
        role = request.form['role']

        cur = mysql.connection.cursor()

        cur.execute("""
            INSERT INTO users
            (full_name, username, email, phone, gender,
            department, address, password, role)

            VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            full_name, username, email, phone,
            gender, department, address,
            password, role
        ))

        mysql.connection.commit()
        cur.close()

        return redirect('/login')

    return render_template('signup.html')

# LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor()

        cur.execute("""
            SELECT * FROM users
            WHERE username=%s AND password=%s
        """, (username, password))

        user = cur.fetchone()

        cur.close()

        if user:
            session['user_id'] = user[0]
            session['name'] = user[1]
            session['role'] = user[9]

            return redirect('/dashboard')

    return render_template('login.html')

# DASHBOARD
@app.route('/dashboard')
def dashboard():

    cur = mysql.connection.cursor()

    cur.execute("SELECT COUNT(*) FROM users")
    total_users = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM projects")
    total_projects = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM tasks")
    total_tasks = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM tasks WHERE status='Completed'")
    completed_tasks = cur.fetchone()[0]

    cur.close()

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

    cur = mysql.connection.cursor()

    if request.method == 'POST':

        project_name = request.form['project_name']
        description = request.form['description']
        deadline = request.form['deadline']
        status = request.form['status']

        cur.execute("""
            INSERT INTO projects
            (project_name,description,deadline,status)

            VALUES(%s,%s,%s,%s)
        """, (
            project_name,
            description,
            deadline,
            status
        ))

        mysql.connection.commit()

    cur.execute("SELECT * FROM projects")
    projects = cur.fetchall()

    cur.close()

    return render_template(
        'projects.html',
        projects=projects
    )

# TASKS
@app.route('/tasks', methods=['GET', 'POST'])
def tasks():

    cur = mysql.connection.cursor()

    if request.method == 'POST':

        task_name = request.form['task_name']
        assigned_to = request.form['assigned_to']
        project_id = request.form['project_id']
        priority = request.form['priority']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        status = request.form['status']

        cur.execute("""
            INSERT INTO tasks
            (task_name,assigned_to,project_id,
            priority,start_date,end_date,status)

            VALUES(%s,%s,%s,%s,%s,%s,%s)
        """, (
            task_name,
            assigned_to,
            project_id,
            priority,
            start_date,
            end_date,
            status
        ))

        mysql.connection.commit()

    cur.execute("""
        SELECT tasks.id,
               tasks.task_name,
               users.full_name,
               projects.project_name,
               tasks.priority,
               tasks.start_date,
               tasks.end_date,
               tasks.status

        FROM tasks

        JOIN users
        ON tasks.assigned_to = users.id

        JOIN projects
        ON tasks.project_id = projects.id
    """)

    tasks = cur.fetchall()

    cur.execute("SELECT * FROM users")
    users = cur.fetchall()

    cur.execute("SELECT * FROM projects")
    projects = cur.fetchall()

    cur.close()

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
    app.run(debug=True)