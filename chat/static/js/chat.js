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

    $('#targetform').submit(function () {
        // act('me', 'vote');
        socket.emit('start day', window.room);
        clear();
        $('#lines').get(0).scrollTop = 10000000;
        return false;
    });

    function clear () {
        $('#message').val('').focus();
    };
});

//code below adapted from https://realpython.com/blog/python/django-and-ajax-form-submissions/

// Submit post on submit
$('#targetform').on('submit', function(event){
    event.preventDefault();
    console.log("form submitted!")  // sanity check
    message('System', "form submitted")
    create_post();
});

// // AJAX for posting
// function create_post() {
//     console.log("create post is working!") // sanity check
//     $.ajax({
//         url : "create_post/", // the endpoint
//         type : "POST", // http method
//         data : { the_post : $('#post-text').val() }, // data sent with the post request

//         // handle a successful response
//         success : function(json) {
//             $('#post-text').val(''); // remove the value from the input
//             console.log(json); // log the returned json to the console
//             console.log("success"); // another sanity check
//         },

//         // handle a non-successful response
//         error : function(xhr,errmsg,err) {
//             $('#results').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: "+errmsg+
//                 " <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
//             console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
//         }
//     });
// };

//code below taken from https://docs.djangoproject.com/en/1.7/ref/contrib/csrf/

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
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
    return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
        (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
        // or any other URL that isn't scheme relative or absolute i.e relative.
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
