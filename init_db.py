import os
import MySQLdb

db = MySQLdb.connect(
    host=os.getenv("MYSQLHOST"),
    user=os.getenv("MYSQLUSER"),
    passwd=os.getenv("MYSQLPASSWORD"),
    db=os.getenv("MYSQLDATABASE"),
    port=int(os.getenv("MYSQLPORT", 3306))
)

cur = db.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100),
    username VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(20),
    password VARCHAR(100),
    role VARCHAR(20)
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS projects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_name VARCHAR(100),
    description TEXT,
    deadline DATE
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    task_name VARCHAR(100),
    assigned_to INT,
    project_id INT,
    priority VARCHAR(20),
    status VARCHAR(50)
)
""")

db.commit()
cur.close()
db.close()

print("Database setup complete")