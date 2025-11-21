// ❌ Vulnerable to Path Traversal
const express = require("express");
const fs = require("fs");
const app = express();

app.get("/read", (req, res) => {
    const filename = req.query.file; // user-controlled
    fs.readFile("./files/" + filename, "utf8", (err, data) => { // ❌ no validation
        if (err) return res.send("Error");
        res.send(data);
    });
});

app.listen(3003, () => console.log("Path traversal app running"));
