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
});

function submitCode(event) {
    event.preventDefault();
    var editor = ace.edit("editor");
    var code = editor.getValue();
    var qid = $('#hid').val();
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