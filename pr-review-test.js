// Sample file to trigger a PR review — has a couple of deliberate issues for the reviewer to catch.

function divide(a, b) {
    return a / b; // no check for b === 0
}

function greet(user) {
    console.log("Hello " + user.name); // no null check on user
}

const password = "hunter2"; // hardcoded secret, should be an obvious flag

module.exports = { divide, greet };
