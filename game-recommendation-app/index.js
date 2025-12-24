const express = require("express");

const app = express();
app.use(express.urlencoded({extended: false}));
app.listen(3000, () => console.log("Listening on http://localhost:3000"));

app.use(express.static("./public"));

// localhost:3000/add-comment
function postAddComment(request, response) {
    console.log(request.body)
    console.log(request.body["user-email"])
    response.redirect("/comment.html")
}

app.post("/add-comment", postAddComment);


// localhost:3000/data
function getData(request, response) {
    response.send([
        Math.random(),
        Math.random()
    ]);
    console.log("the user wants some data")
}

app.get("/get-data", getData);