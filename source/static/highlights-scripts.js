const queryString = window.location.search;
const urlParams = new URLSearchParams(queryString);

let canDrop = true

let options = {
    width: 800,
    height: 450,
    video: urlParams.get('id'),
    parent: ["localhost"]
};
let player = new Twitch.Player("video-player", options);

function seekPlayer(offset) {
    player.seek(parseFloat(offset))
}

function openDrop() {
    document.getElementById('drop-modal').style.display = 'block';
}

function closeDrop() {
    document.getElementById('drop-modal').style.display = 'none';
}

function dropVideo() {
    if (canDrop) {
        canDrop = false;
    }
    else {return;}
    let token = getCookie('csrf_access_token');
    let videoID = urlParams.get('id');
    let modal = document.getElementById('drop-content');
    let loader = document.createElement('div');
    loader.classList.add('loader');
    modal.appendChild(loader);
    let xhr = new XMLHttpRequest();
    xhr.open('POST', '/drop-video', false);
    xhr.setRequestHeader('X-CSRF-TOKEN', token);
    try {
        xhr.send(JSON.stringify({
            'video-id': videoID
        }));
        let response = JSON.parse(xhr.responseText);
        if (xhr.status == 200) {
            window.location.href = '/videos';
        } else {
            alert(response['msg']);
        }
    } catch (err) { // instead of onerror
        alert('Request failed');
    }

}