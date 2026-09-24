from flask import Flask, request
import subprocess
import sqlite3

app = Flask(__name__)


@app.route("/users")
def users():
    department = request.args.get("department")
    conn = sqlite3.connect("directory.db")
    cursor = conn.cursor()
    query = "SELECT * FROM employees WHERE department = '" + department + "'"
    cursor.execute(query)
    return {"rows": cursor.fetchall()}


@app.route("/sync-profile")
def sync_profile():
    employee_id = request.args.get("employee_id")
    result = subprocess.check_output(f"ldapsync --id {employee_id}", shell=True)
    return result.decode()


if __name__ == "__main__":
    app.run(port=5001)
