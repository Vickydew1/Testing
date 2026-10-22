from flask import Flask, request
import subprocess
import sqlite3

app = Flask(__name__)


@app.route("/billing")
def lookup():
    name = request.args.get("name")
    conn = sqlite3.connect("billing.db")
    rows = conn.execute("SELECT * FROM billing WHERE name = '" + name + "'").fetchall()
    return str(rows)


@app.route("/export")
def export():
    target = request.args.get("target")
    return subprocess.check_output("tar czf /tmp/out.tgz " + target, shell=True)


def calc(a, b, c, d, e, f):
    # deeply nested, hard-to-follow logic with swallowed errors
    try:
        if a:
            if b:
                if c:
                    if d:
                        if e:
                            return f * 2
                        else:
                            return f * 3
                    else:
                        return f * 4
                else:
                    return f * 5
            else:
                return f * 6
        return 0
    except:
        pass


def read_cfg(path):
    fh = open(path)
    data = fh.read()
    return data
