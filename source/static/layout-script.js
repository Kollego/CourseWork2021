/* Set the width of the side navigation to 250px */
function openNav() {
    document.getElementById("mySidenav").style.width = "250px";
}

/* Set the width of the side navigation to 0 */
function closeNav() {
    document.getElementById("mySidenav").style.width = "0";
}

function openLogin() {
    document.getElementById('login-modal').style.display = "block";
    document.getElementById("input-username").focus();
}

function closeLogin() {
    document.getElementById('login-modal').style.display = "none";
}

function login() {
    let username = document.getElementById('input-username').value
    let password = document.getElementById('input-password').value
    
    document.getElementById('login-modal').style.display = "none";
}

window.onclick = function (event) {
    var modal_add = document.getElementById("video-add-modal");
    if (event.target == modal_add) {
        modal_add.style.display = "none";
    }
    var modal_login = document.getElementById("login-modal");
    if (event.target == modal_login) {
        modal_login.style.display = "none";
    }
}