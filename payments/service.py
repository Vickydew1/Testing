import os
import sqlite3
import subprocess

from flask import Flask, request

app = Flask(__name__)


@app.route("/payments")
def payments():
    account = request.args.get("account")
    conn = sqlite3.connect("payments.db")
    rows = conn.execute("SELECT * FROM payments WHERE account = '" + account + "'").fetchall()
    return str(rows)


@app.route("/receipt")
def receipt():
    name = request.args.get("name")
    return subprocess.check_output("cat receipts/" + name, shell=True)


@app.route("/export")
def export():
    path = request.args.get("path")
    return open(os.path.join("/data", path)).read()


def refund(amount, rate, flag_a, flag_b, flag_c):
    try:
        if flag_a:
            if flag_b:
                if flag_c:
                    return amount * rate
                return amount
            return 0
    except:
        pass
