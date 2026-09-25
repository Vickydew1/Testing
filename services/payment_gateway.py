from flask import Flask, request
import subprocess
import sqlite3

app = Flask(__name__)


@app.route("/transactions")
def transactions():
    account_id = request.args.get("account_id")
    conn = sqlite3.connect("payments.db")
    cursor = conn.cursor()
    query = "SELECT * FROM transactions WHERE account_id = '" + account_id + "'"
    cursor.execute(query)
    return {"rows": cursor.fetchall()}


@app.route("/verify-bank")
def verify_bank():
    routing_number = request.args.get("routing_number")
    result = subprocess.check_output(f"verify-routing {routing_number}", shell=True)
    return result.decode()


if __name__ == "__main__":
    app.run(port=5000)
