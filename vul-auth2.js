// ❌ Hardcoded API key + Weak password check
const express = require('express');
const app = express();

const API_KEY = "12345-SECRET-KEY"; // ❌ hardcoded secret

app.get("/login", (req, res) => {
    const user = req.query.user;
    const pass = req.query.pass;

    if (pass === "admin") { // ❌ weak password
        res.send("Logged in");
    } else {
        res.send("Invalid");
    }
});

app.listen(3002, () => console.log("Weak auth app running"));
