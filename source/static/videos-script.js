var modal = document.getElementById("video-add-modal");

var btn = document.getElementById("video-add-btn");

var span = document.getElementsByClassName("close")[0];
var get = document.getElementsByClassName("btn-get")[0];

// Создание вкладки с видео
const createVideo = function createVideo(id) {

    let video = document.createElement('div')
    video.classList.add('video')
    video.setAttribute('id', id)
    let image = document.createElement('div')
    image.classList.add('image')
    image.setAttribute('id', 'image' + id)
    let loader = document.createElement('div')
    loader.classList.add('loader')
    loader.setAttribute('id', 'loader' + id)
    let profile = document.createElement('div')
    profile.classList.add('profile-image')
    let name = document.createElement('div')
    name.classList.add('video-name')
    name.setAttribute('id', 'name' + id)
    name.textContent = "#" + id
    let author = document.createElement('div')
    author.classList.add('author')
    author.setAttribute('id', 'author' + id)
    // author.textContent = item.author
    let game = document.createElement('div')
    game.classList.add('game')
    // game.textContent = item.game

    video.appendChild(image)
    video.appendChild(profile)
    video.appendChild(name)
    video.appendChild(author)
    video.appendChild(game)
    image.appendChild(loader)
    video.onclick = function () {
        location.href = '/highlights?id=' + id
    }
    let add = document.getElementById('video-add-btn')
    let grid = add.parentNode;
    grid.insertBefore(video, add)

    return video
};


btn.onclick = function () {
    modal.style.display = "block";
    document.getElementById("input-id").focus();
}

span.onclick = function () {
    modal.style.display = "none";
}

get.onclick = function () {
    let videoID = document.getElementById("input-id").value
    let xhr = new XMLHttpRequest();
    xhr.open("POST", '/get-highlights', true);
    xhr.onload = function () {
        if (xhr.status == 200) {
            var response = JSON.parse(xhr.responseText);
            document.getElementById('name' + videoID).innerText = response["title"];
            document.getElementById('author' + videoID).innerText = response["user_name"];
            document.getElementById('image' + videoID).style.background = "#fff url(" + response['thumbnail_url'] + ") no-repeat center"
            document.getElementById('loader' + videoID).remove()
        } else if (xhr.status == 400) {
            var response = JSON.parse(xhr.responseText);
            alert("Video "+videoID+" not found")
            document.getElementById(videoID).remove();
        }
    }
    // xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(JSON.stringify({
        "video-id": videoID
    }));
    let video = createVideo(videoID)
    modal.style.display = "none";
    document.getElementById("input-id").value = ""
}

window.onclick = function (event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}