// adapted from https://github.com/abourget/gevent-socketio/tree/master/examples/django_chat
// socket.io specific code
var socket = io.connect("/chat");

socket.on('connect', function () {
    $('#chat').addClass('connected');
    socket.emit('join', window.room); 
    $('#starting').hide();
    $('#endphases').hide();
});

socket.on('announcement', function (msg) {
    $('#lines').append($('<p>').append($('<em>').text(msg)));
    $('#lines').get(0).scrollTop = 10000000;
});

socket.on('hide_all', function (msg) {
    $('#actions').hide();
});

socket.on('show_host', function (msg) {
    $('#starting').show();
    $('#endphases').show();
});

socket.on('hide_day', function (msg) {
    $('#voting').hide();
});

socket.on('hide_night', function (msg) {
    $('#nightactions').hide();
});

socket.on('show_day', function (msg) {
    $('#voting').show();
    $('#end-day').show();
    $('#end_night').hide();
    $('#vote').clear();
});

socket.on('show_vote', function (msg) {
    $('#send-vote').show();
});

socket.on('show_night', function (msg) {
    $('#nightactions').show();
    $('#end-day').hide();
    $('#end_night').show();
});

socket.on('hide_mafia', function (msg) {
    $('#targetform').hide();
});

socket.on('hide_cop', function (msg) {
    $('#investigation').hide();
});

socket.on('hide_doctor', function (msg) {
    $('#healing').hide();
});

socket.on('show_self', function (name) {
    $('#info').empty().append('Welcome, ');
    $('#info').append(name).append($('<p>'));
});

socket.on('show_role', function (role) {
    $('#info').append(role);
});

socket.on('regmessage', function (from, msg) {
    // $('#lines').append($('<p>').append($('<b>').text(from), msg));
    message(from, msg)
});

socket.on('nicknames', function (alive, dead) {
    $('#nicknames').empty().append($('<span><b>PLAYERS: </b></span>'));
    for (var i in alive) {
	  $('#nicknames').append($('<p>').text(alive[i]));
    }
    $('#nicknames').append($('<span><b>DEAD: </b></span>'));
    for (var i in dead) {
      $('#nicknames').append($('<p>').text(dead[i]));
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
    $('#lines').get(0).scrollTop = 10000000;
}

function act (from, action) {
    $('#lines').append($('<p>').append($('<b>').text(from), action));
    $('#lines').get(0).scrollTop = 10000000;
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
	    socket.emit('user message', $('#message').val(), window.room);
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

    $('#lock-vote').submit(function () {
        // act('me', 'vote');
        success = socket.emit('vote', $('#vote').val());
        // console.log(str(success));
        if (!success)
        {
            alert("Invalid player. Please vote again.");
        }
        else
        {
            clear();
            $('#lines').get(0).scrollTop = 10000000;
            $('#send-vote').hide();
        }
        
        return false;
    });

    $('#end-day').submit(function () {
        // act('me', 'vote');
        socket.emit('end day', window.room);
        clear();
        $('#lines').get(0).scrollTop = 10000000;
        $('#voting').hide();
        $('#nightactions').show();
        return false;
    });

    $('#start-game').submit(function () {
        // act('me', 'vote');
        socket.emit('start game', window.room);
        clear();
        $('#lines').get(0).scrollTop = 10000000;
        $('#voting').hide();
        $('#starting').hide();
        return false;
    });

    $('#end_night').submit(function () {
        // act('me', 'vote');
        socket.emit('night end', window.room);
        clear();
        $('#lines').get(0).scrollTop = 10000000;
        $('#submit_vote').show();
        $('#voting').show();
        $('#nightactions').hide();
        return false;
    });

    $('#quit').submit(function () {
        // act('me', 'vote');
        socket.emit('quit', window.room);
        clear();
        alert("You have quit the game")
        $('#lines').get(0).scrollTop = 10000000;
        return false;
    });

    $('#investigation').submit(function () {
        // act('me', 'vote');
        alert("investigated!!!!!!")
        socket.emit('investigate', $('#investigate').val());
        clear();
        $('#lines').get(0).scrollTop = 10000000;
        return false;
    });

    function clear () {
        $('#message').val('').focus();
    };
});

//code below taken from https://docs.djangoproject.com/en/1.7/ref/contrib/csrf/
//necessary for AJAX to work with csrf

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length 
                    + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');
 
 
function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
function sameOrigin(url) {
    // test that a given url is a same-origin URL
    // url could be relative or scheme relative or absolute
    var host = document.location.host; // host + port
    var protocol = document.location.protocol;
    var sr_origin = '//' + host;
    var origin = protocol + sr_origin;
    // Allow absolute or scheme relative URLs to same origin
    return (url == origin || url.slice(0, origin.length + 1) == origin + 
        '/') || (url == sr_origin || url.slice(0, sr_origin.length + 
            1) == sr_origin + '/') ||
        // or any other URL that isn't scheme relative or absolute i.e 
        //relative.
        !(/^(\/\/|http:|https:).*/.test(url));
}
 
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
            // Send the token to same-origin, relative URLs only.
            // Send the token only if the method warrants CSRF protection
            // Using the CSRFToken value acquired earlier
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});
