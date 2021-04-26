var options = {
    width: 800,
    height: 450,
    video: "994300889",
    parent: ["localhost"]
};
var player = new Twitch.Player("video-player", options);

function seekPlayer(offset) {
    player.seek(parseFloat(offset))
}
