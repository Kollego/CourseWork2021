/* Set the width of the side navigation to 250px */
function openNav() {
    document.getElementById('mySidenav').style.width = '250px';
}

/* Set the width of the side navigation to 0 */
function closeNav() {
    document.getElementById('mySidenav').style.width = '0';
}

function getCookie(name) {
    let match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
    if (match) return match[2];
    else return '-1';
}

function openLogin() {
    let token = getCookie('csrf_access_token')
    if (token == '-1') {
        document.getElementById('login').style.display = 'block';
        document.getElementById('logout').style.display = 'none';
        document.getElementById('login-modal').style.display = 'block';
        document.getElementById('input-username').focus();
    } else {
        document.getElementById('login').style.display = 'none';
        document.getElementById('logout').style.display = 'block';
        let xhr = new XMLHttpRequest();
        xhr.open('POST', '/identity', false);
        xhr.setRequestHeader('X-CSRF-TOKEN', token)
        try {
            xhr.send();
            if (xhr.status == 200) {
                let response = JSON.parse(xhr.responseText);
                document.getElementById('greetings').innerHTML = 'Hi, ' + response['user'] + '!'
            } else  {
                alert('Token ' + token + ' not found')
            }
        } catch (err) { // instead of onerror
            alert('Request failed');
        }
        document.getElementById('login-modal').style.display = 'block';
    }

}

function closeLogin() {
    document.getElementById('login-modal').style.display = 'none';
}

function login() {
    let username = document.getElementById('input-username').value
    let password = document.getElementById('input-password').value
    let xhr = new XMLHttpRequest();
    xhr.open('POST', '/login', false);
    try {
        xhr.send(JSON.stringify({
            'username': username,
            'password': password
        }));
        if (xhr.status == 200) {
            alert('Successful log in')

        } else if (xhr.status == 400) {
            alert('User ' + username + ' not found')
        }
    } catch (err) { // instead of onerror
        alert('Request failed');
    }

    document.getElementById('login-modal').style.display = 'none';
}

function logout() {
    let xhr = new XMLHttpRequest();
    xhr.open('POST', '/logout', false);
    try {
        xhr.send();
        if (xhr.status == 200) {
            alert('Successful log out')

        } else if (xhr.status == 400) {
            alert('User not found')
        }
    } catch (err) { // instead of onerror
        alert('Request failed');
    }
    document.getElementById('login-modal').style.display = 'none';
}

window.onclick = function (event) {
    let modal_add = document.getElementById('video-add-modal');
    if (event.target == modal_add) {
        modal_add.style.display = 'none';
    }
    let modal_login = document.getElementById('login-modal');
    if (event.target == modal_login) {
        modal_login.style.display = 'none';
    }
}