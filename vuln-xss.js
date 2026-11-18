// ❌ Reflected XSS
const express = require("express");
const app = express();

app.get("/", (req, res) => {
    const name = req.query.name || "Guest";
    res.send(`<h1>Hello ${name}</h1>`); // ❌ direct injection → XSS
});

app.listen(3004, () => console.log("XSS vulnerable app running"));










