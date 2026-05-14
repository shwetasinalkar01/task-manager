import pymysql
import os


def get_db():
    return pymysql.connect(
        host=os.getenv("MYSQLHOST"),
        user=os.getenv("MYSQLUSER"),
        password=os.getenv("MYSQLPASSWORD"),
        database=os.getenv("MYSQLDATABASE"),
        port=int(os.getenv("MYSQLPORT", 3306)),
        autocommit=True
    )


def init_db():
    conn = get_db()
    cur = conn.cursor()

    # USERS
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

    # PROJECTS
    cur.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id INT AUTO_INCREMENT PRIMARY KEY,
        project_name VARCHAR(255),
        description TEXT,
        deadline DATE,
        status VARCHAR(50)
    )
    """)

    # TASKS
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
    print("✅ Database Initialized Successfully")


if __name__ == "__main__":
    init_db()