var modal = document.getElementById('video-add-modal');

var btn = document.getElementById('video-add-btn');

var span = document.getElementById('close-add');
var get = document.getElementById('btn-get-add');

// Создание вкладки с видео
const createVideo = function createVideo(id) {
    if (document.getElementById(id)) {
        return
    }
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
    profile.setAttribute('id', 'profile' + id)
    let name = document.createElement('div')
    name.classList.add('video-name')
    name.setAttribute('id', 'name' + id)
    name.textContent = '#' + id
    let author = document.createElement('div')
    author.classList.add('author')
    author.setAttribute('id', 'author' + id)

    video.appendChild(image)
    video.appendChild(profile)
    video.appendChild(name)
    video.appendChild(author)
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
    modal.style.display = 'block';
    document.getElementById('input-id').focus();
}

span.onclick = function () {
    modal.style.display = 'none';
}

get.onclick = function () {
    let videoID = document.getElementById('input-id').value.trim()
    let xhr = new XMLHttpRequest();
    let token = getCookie('csrf_access_token')
    xhr.open('POST', '/get-highlights', true);
    xhr.setRequestHeader('X-CSRF-TOKEN', token)
    xhr.onload = function () {
        if (xhr.status == 200) {
            let response = JSON.parse(xhr.responseText);
            document.getElementById('name' + videoID).innerText = response['title'];
            document.getElementById('author' + videoID).innerText = response['user_name'];
            document.getElementById('image' + videoID).style.background = '#fff url(' + response['thumbnail_url'] + ') no-repeat center';
            //document.getElementById('loader' + videoID).remove();
            document.getElementById('profile' + videoID).style.background = '#fff url(' + response['profile_image'] + ') no-repeat center';
            document.getElementById('profile' + videoID).style.backgroundSize = 'cover';
        } else if (xhr.status == 400) {
            let response = JSON.parse(xhr.responseText);
            alert(response['msg'])
            document.getElementById(videoID).remove();
        } else if (xhr.status == 401) {
            let response = JSON.parse(xhr.responseText);
            alert(response['msg'])
        }
    }
    // xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(JSON.stringify({
        'video-id': videoID
    }));
    let video = createVideo(videoID)
    modal.style.display = 'none';
    document.getElementById('input-id').value = ''
}

function highlights(id) {
    document.location.href = '/highlights?id='+id
}
