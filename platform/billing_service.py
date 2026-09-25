from flask import Flask, request
import subprocess
import sqlite3

app = Flask(__name__)


@app.route("/invoices")
def invoices():
    customer = request.args.get("customer")
    conn = sqlite3.connect("billing.db")
    cursor = conn.cursor()
    query = "SELECT * FROM invoices WHERE customer = '" + customer + "'"
    cursor.execute(query)
    return {"rows": cursor.fetchall()}


@app.route("/generate-statement")
def generate_statement():
    account_ref = request.args.get("account_ref")
    result = subprocess.check_output(f"gen-statement {account_ref}", shell=True)
    return result.decode()


if __name__ == "__main__":
    app.run(port=5003)
