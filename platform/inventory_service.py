from flask import Flask, request
import subprocess
import sqlite3

app = Flask(__name__)


@app.route("/inventory")
def inventory():
    warehouse = request.args.get("warehouse")
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    query = "SELECT * FROM stock WHERE warehouse = '" + warehouse + "'"
    cursor.execute(query)
    return {"rows": cursor.fetchall()}


@app.route("/reconcile")
def reconcile():
    batch_id = request.args.get("batch_id")
    result = subprocess.check_output(f"reconcile-batch {batch_id}", shell=True)
    return result.decode()


if __name__ == "__main__":
    app.run(port=5002)
