// adapted from https://github.com/abourget/gevent-socketio/tree/master/examples/django_chat
// socket.io specific code
var socket = io.connect("/chat");

socket.on('connect', function () {
    $('#chat').addClass('connected');
    socket.emit('join', window.room); 
});

socket.on('announcement', function (msg) {
    $('#lines').append($('<p>').append($('<em>').text(msg)));
});

socket.on('nicknames', function (nicknames) {
    $('#nicknames').empty().append($('<span>Players: </span>'));
    for (var i in nicknames) {
	  $('#nicknames').append($('<p>').text(nicknames[i]));
    }
});

socket.on('msg_to_room', message);

socket.on('reconnect', function () {
    $('#lines').remove();
    message('System', 'Reconnected to the server');
});

socket.on('reconnecting', function () {
    message('System', 'Attempting to re-connect to the server');
});

socket.on('error', function (e) {
    message('System', e ? e : 'A unknown error occurred');
});

function message (from, msg) {
    $('#lines').append($('<p>').append($('<b>').text(from), msg));
}

function act (from, action) {
    $('#lines').append($('<p>').append($('<b>').text(from), action));
}

// DOM manipulation
$(function () {
    $('#set-nickname').submit(function (ev) {
        socket.emit('nickname', $('#nick').val(), window.room, function (set) {
            if (set) {
                clear();
                return $('#chat').addClass('nickname-set');
            }
            $('#nickname-err').css('visibility', 'visible');
        });
        return false;
    });

    $('#send-message').submit(function () {
	    message('me', $('#message').val());
	    socket.emit('user message', $('#message').val());
	    clear();
	    $('#lines').get(0).scrollTop = 10000000;
	    return false;
    });

    $('#send-action').submit(function () {
        // act('me', 'investigate');
        socket.emit('investigate', 'name');
        clear();
        $('#lines').get(0).scrollTop = 10000000;
        return false;
    });

    $('#send-vote').submit(function () {
        // act('me', 'vote');
        socket.emit('vote', $('#vote').val());
        clear();
        $('#lines').get(0).scrollTop = 10000000;
        return false;
    });

    $('#start-game').submit(function () {
        // act('me', 'vote');
        socket.emit('start game', window.room);
        clear();
        $('#lines').get(0).scrollTop = 10000000;
        return false;
    });

    function clear () {
        $('#message').val('').focus();
    };
});
