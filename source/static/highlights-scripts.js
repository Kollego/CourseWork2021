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

let highlights = document.getElementsByClassName('highlight')

function toHex(rgb) {
    let hex = Number(rgb).toString(16);
    if (hex.length < 2) {
        hex = "0" + hex;
    }
    return hex;
};

function getColor(weight) {
    let color1 = [136, 52, 252]
    let color2 = [255, 255, 255]
    let w1 = weight;
    let w2 = 1 - w1;
    let color = [toHex(Math.round(color1[0] * w1 + color2[0] * w2)),
        toHex(Math.round(color1[1] * w1 + color2[1] * w2)),
        toHex(Math.round(color1[2] * w1 + color2[2] * w2))];
    return '#' + color[0] + color[1] + color[2];
}

let i;
for (i = 0; i < highlights.length; i++) {
    let score = parseInt(highlights[i].dataset.score) / 100;

    highlights[i].style.backgroundColor = getColor(score);
}

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
    } else {
        return;
    }
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

function sortHighlights(order) {
    let hlist = document.getElementsByClassName('highlight-list')[0];
    let highlights = hlist.children;
    highlights = Array.prototype.slice.call(highlights);
    if (order == 'time') {
        highlights.sort(function (a, b) {
            return a.textContent.localeCompare(b.textContent);
        });
        document.getElementById('time-btn').style.backgroundColor = '#8834fc'
        document.getElementById('score-btn').style.backgroundColor = '#818181'

    } else {
        highlights.sort(function (a, b) {
            let scoreA = parseInt(a.dataset.score);
            let scoreB = parseInt(b.dataset.score);
            if (scoreA < scoreB) return 1;
            else return -1;
        });
        document.getElementById('score-btn').style.backgroundColor = '#8834fc'
        document.getElementById('time-btn').style.backgroundColor = '#818181'
    }
    for (let i = 0, len = highlights.length; i < len; i++) {
        let parent = highlights[i].parentNode;
        let detatchedItem = parent.removeChild(highlights[i]);
        parent.appendChild(detatchedItem);
    }
}