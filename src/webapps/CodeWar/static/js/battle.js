$(document).ready(function () {  // Runs when the document is ready
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
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

    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
    $("#submit").on("click", submitCode);
    $("#test").on("click", testCode);
    $("#syn").on('click', synCode);
    $("help").on('click', getChat);
});

function synCode(event) {
    $.get("/codewar/getcode/" + $('#teammate').val() + "/" + $('#hid').val())
        .done(function (data) {
            var session = editor.session;
            session.insert({
                row: session.getLength(),
                column: 0
            }, "\n\n\n#" + $('#teammate').val() + ":\n" + data['code']);
        });
}

function submitCode(event) {
    event.preventDefault();
    var editor = ace.edit("editor");
    var code = editor.getValue();
    var qid = $('#hid').val();
    setCode();
    $.post("/codewar/run/" + qid, {"code": code})
        .done(function (data) {
                $('.nav-tabs a[href="#menu2"]').tab('show');
                var count = data['count'];
                move(count);
                $('#rl').empty();
                var l = $('#rl');
                for (var i = 0; i < data['result'].length; i++) {
                    var r = "";
                    if (data['result'][i]['show'].length != 0) {
                        r += "<li class='list-group-item list-group-item-danger'><p>" + data['result'][i]['output'] + "</p>";
                    } else {
                        r += "<li class='list-group-item list-group-item-success'><p>" + data['result'][i]['output'] + "</p>";
                    }
                    if (data['result'][i]['show'].length != 0) {
                        r += "<p>" + data['result'][i]['show'] + "</p></li>";
                    }

                    l.append(r);
                }

            }
        );
}

function move(count) {
    var elem = document.getElementById("myBar");
    elem.style.width = 0;
    elem.innerHTML = 0 + '%';
    var width = 0;
    var id = setInterval(frame, 0);

    function frame() {
        if (width >= count / 6 * 100) {
            clearInterval(id);
        } else {
            width++;
            elem.style.width = width + '%';
            elem.innerHTML = width * 1 + '%';
        }
    }

    setScore(count);
}

function testCode() {
    event.preventDefault();
    var editor = ace.edit("editor");
    var code = editor.getValue();
    var testcase = $("#test-case").val();
    var qid = $('#hid').val();
    $.post("/codewar/test/" + qid, {"code": code, "case": testcase})
        .done(function (data) {
            $('.nav-tabs a[href="#menu2"]').tab('show');
            $('#rl').empty();
            var l = $('#rl');
            var r = "";
            r += "<p>Your Output: " + data['output'] + "</p>";
            r += "<p>" + data['error'] + "</p><br>";
            l.append(r);
        });
}

function setCode() {
    var editor = ace.edit("editor");
    var code = editor.getValue();
    $.post("/codewar/setcode/" + $('#hid').val(), {"code": code});
}

function setScore(count) {
    $.post("/codewar/setscore/" + $('#roomname').val() + "/" + $('#hid').val() + "/" + $('#another').val(), {'score': count})
        .done(function (data) {
            $('#score').text(data['score']);
            if (data['success'].toString() === "1") {
                window.location.href = "/codewar/success";
                console.log($('#roomname').val() + "  here");
            }
        });
}

function getScore() {
    $.get("/codewar/getscore/" + $('#roomname').val() + "/" + $('#hid').val() + "/" + $('#another').val())
        .done(function (data) {
            $('#score').text(data['score']);
            console.log(data['success']);
            if (data['success'].toString() === "1") {
                clear();
                console.log($('#roomname').val() + "  there");
                window.location.href = "/codewar/success";
            }
        });
}

function clear() {
    $.post('/codewar/clear', {
        'qid1': $('#hid').val(),
        'qid2': $('#another').val(),
        'roomname': $('#roomname').val(),
        'teammate': $('#teammate').val()
    })
}

function getResult() {
    $.get('/codewar/result/' + $('#roomname').val())
        .done(function (data) {
            console.log($('#roomname').val() + "  " + data['success']);
            if (data['success'].toString() === "1") {
                window.location.href = "/codewar/loss";
            }
        })

}

function getChat() {
    console.log($('#chat-log').text());
    $.post('/codewar/savechat', {'roomname': $('#roomname').val(), 'chat': $('#chat-log').val()});
}

window.setInterval(setCode, 10000);

window.setInterval(getResult, 7000);

window.setInterval(getScore, 8000);