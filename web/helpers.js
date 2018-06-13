var songIds = [];
var YOUTUBE_EMBED_SCRIPT = `<iframe width="560" height="315" src="https://www.youtube.com/embed/{ID}?autoplay=1;?rel=0" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>`;
var socket = getSocketConnection()
var player;
var reconnectOnConnectionLost = true;
var playing = false;

setInterval(() => {
    if (socket.readyState === socket.CLOSED) {
        socket = getSocketConnection();
    }
}, 3000);


setInterval(() => {
    if (hasNextSong() && !playing) {
        playNextSong();
        playing = true;
    }
}, 1000);

function removeYoutubePlayer() {
    document.getElementById("yt-container").innerHTML = "<div id='yt'></id>";
}

function updateYoutubeEmbeded(id) {
    removeYoutubePlayer();

    player = new YT.Player('yt', {
        height: '390',
        width: '640',
        videoId: id,
        events: {
            'onReady': e => {
                e.target.playVideo();
            },
            'onStateChange': e => {
                switch (e.data) {
                    case YT.PlayerState.ENDED:
                        document.getElementById("yt-container").innerHTML = "";
                        playing = false;
                        break;
                }
            },
            'onError': e => {
                playNextSong();
            }
        }
    });
}

function onYouTubeIframeAPIReady() {
    // updateYoutubeEmbeded();
}

function nextSongId() {
    return songIds.length ? songIds.shift() : -1;
}

function hasNextSong() {
    return songIds.length != 0;
}

function playNextSong() {
    if (hasNextSong()) {
        updateYoutubeEmbeded(nextSongId());
    }
    else {
        removeYoutubePlayer();
    }
}

function extractSongId(str) {
    var split = str.split(' ');

    if (split[0] === 'PLAY') {
        split.shift();
        return split.join(' ');
    }
}

function getSocketConnection() {
    var socket = new WebSocket("ws://localhost:9999");

    socket.onerror = e => {
        console.log(`SOCKET ERROR: ${e}`);
    }
    socket.onclose = e => {
        console.log(`SOCKET CLOSED: ${e}`);
    }
    socket.onopen = e => {
        console.log(`SOCKET OPEN: ${e}`)
    }
    socket.onmessage = e => {
        id = extractSongId(e.data);

        if (id) {
            songIds.push(id);
        }
        else if (e.data === 'SKIP'){
            playNextSong();
        }
    }

    return socket;
}

