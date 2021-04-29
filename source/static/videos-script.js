var modal = document.getElementById("video-add-modal");

var btn = document.getElementById("video-add-btn");

var span = document.getElementsByClassName("close")[0];
var get = document.getElementsByClassName("btn-get")[0];

const createVideo = function createVideo(item) {

    let video = document.createElement('div')
    video.classList.add('video')
    let image = document.createElement('div')
    image.classList.add('image')
    let profile = document.createElement('div')
    profile.classList.add('profile-image')
    let name = document.createElement('div')
    name.classList.add('video-name')
    name.textContent = item.name
    let author = document.createElement('div')
    author.classList.add('author')
    author.textContent = item.author
    let game = document.createElement('div')
    game.classList.add('game')
    game.textContent = item.game

    video.appendChild(image)
    video.appendChild(profile)
    video.appendChild(name)
    video.appendChild(author)
    video.appendChild(game)

    var add = document.getElementById('video-add-btn')
    var grid = add.parentNode;
    grid.insertBefore(video, add)
};

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
    item = {name: 'TESTNAME', author: 'AUTHOR', game: 'GAME'}
    createVideo(item)
    modal.style.display = "none";
}

window.onclick = function (event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}