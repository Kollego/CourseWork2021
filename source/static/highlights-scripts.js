const queryString = window.location.search;
const urlParams = new URLSearchParams(queryString);

var options = {
    width: 800,
    height: 450,
    video: urlParams.get('id'),
    parent: ["localhost"]
};
var player = new Twitch.Player("video-player", options);

function seekPlayer(offset) {
    player.seek(parseFloat(offset))
}
