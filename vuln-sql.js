// ❌ Vulnerable code — SQL Injection
const express = require("express");
const mysql = require("mysql");
const app = express();

const db = mysql.createConnection({
    host: "localhost",
    user: "root",
    password: "",
    database: "testdb"
});

app.get("/user", (req, res) => {
    const id = req.query.id;  // user-controlled
    const query = `SELECT * FROM users WHERE id = '${id}'`; // ❌ vulnerable
    db.query(query, (err, result) => {
        if (err) res.send("Error");
        res.json(result);
    });
});

// Added for the PR Decorator demo — second injection point
app.get("/search", (req, res) => {
    const term = req.query.term;  // user-controlled
    const query = "SELECT * FROM products WHERE name = '" + term + "'"; // ❌ vulnerable
    db.query(query, (err, result) => {
        if (err) res.send("Error");
        res.json(result);
    });
});

app.listen(3001, () => console.log("Vulnerable SQL app running"));
