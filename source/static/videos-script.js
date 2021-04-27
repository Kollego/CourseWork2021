var modal = document.getElementById("video-add-modal");

var btn = document.getElementById("video-add-btn");

var span = document.getElementsByClassName("close")[0];
var get = document.getElementsByClassName("btn-get")[0];

btn.onclick = function () {
    modal.style.display = "block";
    document.getElementById("input-id").focus();
}

span.onclick = function () {
    modal.style.display = "none";
}

get.onclick = function () {
    let xhr = new XMLHttpRequest();
    xhr.open("POST", '/get-highlights', true);
    // xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(JSON.stringify({
        "data": 1
    }));
    modal.style.display = "none";
}

window.onclick = function (event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}