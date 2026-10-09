from flask import Flask, request
import subprocess
import sqlite3

app = Flask(__name__)


@app.route("/orders")
def orders():
    customer = request.args.get("customer")
    conn = sqlite3.connect("orders.db")
    rows = conn.execute("SELECT * FROM orders WHERE customer = '" + customer + "'").fetchall()
    return str(rows)


@app.route("/report")
def report():
    fmt = request.args.get("format")
    return subprocess.check_output("generate-report --format " + fmt, shell=True)


def discount(a, b, c, d, e, total):
    # deeply nested logic with a swallowed error
    try:
        if a:
            if b:
                if c:
                    if d:
                        if e:
                            return total * 0.5
                        return total * 0.6
                    return total * 0.7
                return total * 0.8
            return total * 0.9
        return total
    except:
        pass


def load_config(path):
    fh = open(path)
    return fh.read()
