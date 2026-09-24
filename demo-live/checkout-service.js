// Live demo — checkout service with a couple of intentional issues
const express = require("express");
const mysql = require("mysql");
const app = express();

const db = mysql.createConnection({
    host: "localhost",
    user: "root",
    password: "",
    database: "orders",
});

// SQL injection — order lookup by user-controlled id
app.get("/orders", (req, res) => {
    const userId = req.query.userId;
    const query = "SELECT * FROM orders WHERE user_id = '" + userId + "'";
    db.query(query, (err, result) => {
        if (err) res.send("Error");
        res.json(result);
    });
});

// Command injection — export order to a user-controlled filename
const { exec } = require("child_process");
app.get("/export", (req, res) => {
    const filename = req.query.filename;
    exec("cp orders.csv " + filename, (err) => {
        res.send(err ? "Export failed" : "Export complete");
    });
});

// Lookup order by user-controlled reference number
app.get("/order-lookup", (req, res) => {
    const ref = req.query.ref;
    const query = "SELECT * FROM orders WHERE reference = '" + ref + "'";
    db.query(query, (err, result) => {
        if (err) res.send("Error");
        res.json(result);
    });
});

app.listen(3003, () => console.log("Checkout service running"));
