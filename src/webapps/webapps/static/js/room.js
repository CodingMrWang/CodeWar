$('document').ready(function () {

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


    var room_id = $('#room_id_indicator')[0].value;
    var personal_username = $('#username_indicator')[0].value;
    var personal_url = $('#user_url_indicator')[0].value;
    var chatSocket = new WebSocket(
        'ws://' + window.location.host +
        '/ws/chat/' + room_id + '/');


    chatSocket.onopen = function (e) {
        chatSocket.send(JSON.stringify({
            "newarrival": "arrival",
            "room_id": room_id
        }));
    };


    var heartbeat_updating = setInterval(function () {
        $.ajax({
            url: "/codewar/updatePosition/" + room_id,
            dataType: "json",
            headers: {
                "X-CSRFToken": csrftoken
            },
            type: 'GET',
            method: "GET",
            success: function (response) {

                for (var i = 1; i <= 4; i++) {

                    var username = "user" + i + "_username";
                    $('#user_name_indicator' + i)[0].value = response[username];
                }
                for (var i = 2; i <= 4; i++) {
                    $("#user" + i).find('.personal-photo-hyperlink').find('img')[0].src = response["user" + i + "_url"];
                    $("#user" + i).find('.user-status')[0].innerHTML = response["user" + i + "_state"];
                    if ($("#user" + i).find('.card-img-right.flex-auto.d-none.d-lg-block')[0].src !== response["user" + i + "_state_url"]) {
                        $("#user" + i).find('.card-img-right.flex-auto.d-none.d-lg-block')[0].src = response["user" + i + "_state_url"];
                    }
                }

            }
        });
    }, 1000);
    chatSocket.onmessage = function (e) {
        var data = JSON.parse(e.data);
        if (data['new_status'] !== undefined) {
            for (var i = 1; i <= 4; i++) {
                var username = "user" + i + "_username";
                $('#user_name_indicator' + i)[0].value = data[username];
            }

            var position = data['position'];
            var status = data['new_status'];
            var status_url = data['new_status_url'];
            $("#" + position).find('.user-status')[0].innerHTML = status;
            $("#" + position).find('.card-img-right.flex-auto.d-none.d-lg-block')[0].src = status_url;

            var status1 = $("#user1").find('.user-status')[0].innerHTML;
            var status2 = $("#user2").find('.user-status')[0].innerHTML;
            var status3 = $("#user3").find('.user-status')[0].innerHTML;
            var status4 = $("#user4").find('.user-status')[0].innerHTML;
            if (status1 === "ready" && status2 === "ready" && status3 === "ready" && status4 === "ready") {

                var username1_test = $('#user_name_indicator1')[0].value;
                var username2_test = $('#user_name_indicator2')[0].value;
                var username3_test = $('#user_name_indicator3')[0].value;
                var username4_test = $('#user_name_indicator4')[0].value;
                if (username1_test === personal_username) {
                    var username2_test = $('#user_name_indicator2')[0].value;
                    window.location.pathname = "codewar/startbattle/" + room_id + "-alpha/" + personal_username + "-" + username2_test;
                }
                else if (username2_test === personal_username) {
                    var username1_test = $('#user_name_indicator1')[0].value;
                    window.location.pathname = "codewar/startbattle/" + room_id + "-alpha/" + personal_username + "-" + username1_test;
                }
                else if (username3_test === personal_username) {
                    var username4_test = $('#user_name_indicator4')[0].value;
                    window.location.pathname = "codewar/startbattle/" + room_id + "-beta/" + personal_username + "-" + username4_test;
                }
                else if (username4_test === personal_username) {
                    var username3_test = $('#user_name_indicator3')[0].value;
                    window.location.pathname = "codewar/startbattle/" + room_id + "-beta/" + personal_username + "-" + username3_test;
                }
            }

        } else if (data['newarrival'] !== undefined) {
            var position = data['position'];
            var url = data['url'];
            var status = data['status'];
            var status_url = data['status_url'];


            $("#" + position).find('.personal-photo-hyperlink').find('img')[0].src = url;
            $("#" + position).find('.user-status')[0].innerHTML = status;
            $("#" + position).find('.card-img-right.flex-auto.d-none.d-lg-block')[0].src = status_url;
        }
        else if (data['message'] !== undefined) {
            var message = data['message'];
            var initial = data['initial'];
            var modify = data['modify'];

            if (message !== "nochange") {
                if ($("#" + modify).find('.personal-photo-hyperlink').find('img')[0].src !== "") {
                    var initialImage = $("#" + initial).find('.personal-photo-hyperlink').find('img')[0].src;

                    $("#" + modify).find('.user-status')[0].innerHTML = "preparing";
                    $("#" + modify).find('.card-img-right.flex-auto.d-none.d-lg-block')[0].src = "https://media.giphy.com/media/9g1h1BQx9a55m/giphy.gif";
                    $("#" + modify).find('.personal-photo-hyperlink').find('img')[0].src = initialImage;

                    $("#" + initial).find('.personal-photo-hyperlink').find('img')[0].src = "";
                    $("#" + initial).find('.user-status')[0].innerHTML = "";
                    $("#" + initial).find('.card-img-right.flex-auto.d-none.d-lg-block')[0].src = "";
                }
            }
        }
        else if (data['exit_user'] !== undefined) {

            var exit_user = data['exit_user'];

            if (data['adjusted_user'] !== "nouser") {

                var adjust_user = data['adjusted_user'];
                var adjusted_status = $("#" + adjust_user).find('.user-status')[0].innerHTML;
                var adjusted_gif = $("#" + adjust_user).find('.card-img-right.flex-auto.d-none.d-lg-block')[0].src;
                var user_photo = $("#" + adjust_user).find('.personal-photo-hyperlink').find('img')[0].src;
                $("#" + exit_user).find('.personal-photo-hyperlink').find('img')[0].src = user_photo;
                $("#" + exit_user).find('.user-status')[0].innerHTML = adjusted_status;
                $("#" + exit_user).find('.card-img-right.flex-auto.d-none.d-lg-block')[0].src = adjusted_gif;
                $('.room-active-user')[0].src = user_photo;
                $("#" + adjust_user).find('.personal-photo-hyperlink').find('img')[0].src = "";
                $("#" + adjust_user).find('.user-status')[0].innerHTML = "";
                $("#" + adjust_user).find('.card-img-right.flex-auto.d-none.d-lg-block')[0].src = "";

            } else {
                $("#" + exit_user).find('.personal-photo-hyperlink').find('img')[0].src = "";
                $("#" + exit_user).find('.user-status')[0].innerHTML = "";
                $("#" + exit_user).find('.card-img-right.flex-auto.d-none.d-lg-block')[0].src = "";
            }

        }
        else if (data['disconnection_update'] !== undefined) {
            for (var i = 1; i <= 4; i++) {
                if (data["user" + i + "_url"] !== "") {
                    $("#user" + i).find('.personal-photo-hyperlink').find('img')[0].src = "/codewar" + data["user" + i + "_url"];
                    $("#user" + i).find('.user-status')[0].innerHTML = data["user" + i + "_status"];
                    $("#user" + i).find('.card-img-right.flex-auto.d-none.d-lg-block')[0].src = data["user" + i + "_status_url"];
                } else {
                    $("#user" + i).find('.personal-photo-hyperlink').find('img')[0].src = data["user" + i + "_url"];
                    $("#user" + i).find('.user-status')[0].innerHTML = data["user" + i + "_status"];
                    $("#user" + i).find('.card-img-right.flex-auto.d-none.d-lg-block')[0].src = data["user" + i + "_status_url"];
                }

            }


        } else if (data['room_acces_symbol'] !== undefined) {
            $('#room-status-indicator')[0].innerHTML = data['room_acces_symbol'];
        }
    };


    chatSocket.onclose = function (e) {
        console.error('Chat socket closed unexpectedly');
    };


    // these are the methods for changing the seats in the room...
    document.querySelector('#start-btn').onclick = function (e) {

        chatSocket.send(JSON.stringify({
            "userstatus": "change",
            "room_id": room_id
        }));
    };

    document.querySelector('#second-link-indicator').onclick = function (e) {


        if (!$('.personal-photo-hyperlink').find('img')[2].src.includes('media')) {

            var sendData = {
                "change": "user2",
                "room_id": room_id
            };

            $.ajax({
                url: "/codewar/changePosition",
                dataType: "json",
                headers: {
                    "X-CSRFToken": csrftoken
                },
                data: sendData,
                type: 'POST',
                method: "POST"
            });
        }
    };

    document.querySelector('#third-link-indicator').onclick = function (e) {
        if (!$('.personal-photo-hyperlink').find('img')[1].src.includes('media')) {

            var sendData = {
                "change": "user3",
                "room_id": room_id
            };
            $.ajax({
                url: "/codewar/changePosition",
                dataType: "json",
                headers: {
                    "X-CSRFToken": csrftoken
                },
                data: sendData,
                type: 'POST',
                method: "POST"
            });
        }
    };

    document.querySelector('#fourth-link-indicator').onclick = function (e) {

        if (!$('.personal-photo-hyperlink').find('img')[0].src.includes('media')) {

            var sendData = {
                "change": "user4",
                "room_id": room_id
            };
            $.ajax({
                url: "/codewar/changePosition/",
                dataType: "json",
                headers: {
                    "X-CSRFToken": csrftoken
                },
                data: sendData,
                type: 'POST',
                method: "POST"
            });
        }
    };

    // these are the methods for changing the seats in the room...


    document.querySelector('#exit-btn').onclick = function (e) {
        chatSocket.send(JSON.stringify({
            "exit": "true",
            "room_id": room_id
        }));
        window.location.pathname = "/codewar";
    };

    $(document).on('click', '.notification-envelop', function () {
        if ($('#exampleModalLabel')[0].innerHTML === "Your invitation has been sent out.") {
            $('#myModal').empty();
            $('#myModal').append(
                "  <div class=\"modal-dialog\" role=\"document\">\n" +
                "    <div class=\"modal-content\">\n" +
                "      <div class=\"modal-header\">\n" +
                "        <h5 class=\"modal-title\" id=\"exampleModalLabel\">Invite a User to join.</h5>\n" +
                "        <button type=\"button\" class=\"close\" data-dismiss=\"modal\" aria-label=\"Close\">\n" +
                "          <span aria-hidden=\"true\">&times;</span>\n" +
                "        </button>\n" +
                "      </div>\n" +
                "\n" +
                "      <div class=\"modal-body\">\n" +
                "        <div>\n" +
                "       <input type=\"search\" id=\"search-user\" placeholder=\"please type in user name to search\">\n" +
                "     </div>\n" +
                "     <div id=\"searchDiv\">\n" +
                "       <button class=\"room-status\" id=\"search-user-button\">go search it</button>\n" +
                "     </div>\n" +
                "     <div>\n" +
                "       <textarea id=\"invitation-content\" placeholder=\"write some words to your invitee...\" max_length=\"20\"></textarea></div>\n" +
                "      <div class=\"modal-footer\">\n" +
                "        <button type=\"button\" class=\"btn btn-secondary\" data-dismiss=\"modal\">Close</button>\n" +
                "        <button type=\"button\" class=\"btn btn-primary\" id=\"send-invitation-btn\">Send</button>\n" +
                "      </div>\n" +
                "    </div>\n" +
                "  </div>\n" +
                "</div>");

        }
        $('#myModal').appendTo('body').modal('show');
    });

    $('body').on('click', '#search-user-button', function () {
        var search_term = $("#search-user").val();
        $.ajax({
            url: "/codewar/searchUser",
            dataType: "json",
            headers: {
                "X-CSRFToken": csrftoken
            },
            data: {'search_term': search_term},
            type: 'POST',
            method: "POST",
            success: function (response) {
                loadUsers(response);
            }
        });
    });

    $('body').on('change', '#toggle-event', function (event) {
        var room_id = $('#room_id_indicator')[0].value;

        var username1_test = $('#user_name_indicator1')[0].value;
        
        if (personal_username === username1_test) {
            $.ajax({
                url: "/codewar/changeRoomStatus",
                dataType: "json",
                headers: {
                    "X-CSRFToken": csrftoken
                },
                data: {"room_id": room_id},
                type: 'POST',
                method: "POST",
                success: function (response) {
                    if (response['response'] === 'nochange') {
                        return;
                    }
                    if (response['response'] === 'topublic') {
                        $('#room-status-indicator')[0].innerHTML = "Public Room";

                        chatSocket.send(JSON.stringify({
                            "room_acces_symbol": "Public Room",
                            "room_id": room_id
                        }));
                    }
                    else if (response['response'] === 'toprivate') {

                        chatSocket.send(JSON.stringify({
                            "room_acces_symbol": "Private Room",
                            "room_id": room_id
                        }));

                        $('#room-status-indicator')[0].innerHTML = "Private Room";
                    }
                }
            });
        }

    });

    function changePositionMeta(input_user) {
    }

    function loadUsers(data) {
        $('#table-with-users').empty();
        if ($('#table-with-users').length === 0) {
            var tobeAppend = "<div class=\"display_result\">\n" +
                "<table class=\"the-result-table\" id='table-with-users'>";

            var data_list = data['users'];
            for (var i = 0; i < data_list.length; i++) {
                var username = data_list[i]['username'];
                var url = data_list[i]['photo_url'];
                var eachRow = "<tr><td class='username-column'>" + username + "</td>" +
                    "<td><img class=\"each_source_right\" src=\"/codewar" + url + "\"></td>" +
                    "<td><button class='select-user1'>Select</button></td></tr>";
                tobeAppend += eachRow;
            }
            tobeAppend += "</table></div>";
            $('#searchDiv').after(tobeAppend);
        }
        if ($("#table-with-users").length === 1) {
            $('#table-with-users').empty();
            var data_list = data['users'];
            var tobeAppend = "";
            for (var i = 0; i < data_list.length; i++) {
                var username = data_list[i]['username'];
                var url = data_list[i]['photo_url'];
                var eachRow = "<tr><td class='username-column'>" + username + "</td>" +
                    "<td><img class=\"each_source_right\" src=\"/codewar" + url + "\"></td>" +
                    "<td><button class='select-user1'>Select</button></td></tr>";
                tobeAppend += eachRow;
            }
            $('#table-with-users').append(tobeAppend);
        }
    }

    $('body').on('click', '.select-user1', function () {
        var selected = $(this).parent().before().before().parent().html();
        $('.the-result-table').empty();
        $('.the-result-table').append(selected);
        $('.select-user1')[0].innerHTML = "Selected";
    });

    $('body').on('click', '#send-invitation-btn', function () {
        var send_content = $('#invitation-content').val();
        var checkUsers = $("#table-with-users").find(".username-column").length;
        if (checkUsers === 1) {
            var username = $("#table-with-users").find(".username-column")[0].innerHTML;
            var room_id = $('#room_id_indicator').val();
            $.ajax({
                url: "/codewar/createInvitation",
                dataType: "json",
                headers: {
                    "X-CSRFToken": csrftoken
                },
                data: {
                    'invitee': username,
                    'messgae': send_content,
                    'room-id': room_id
                },
                type: 'POST',
                method: "POST",
                success: function (response) {
                    $('.modal-body').empty();
                    $('#exampleModalLabel')[0].innerHTML = "Your invitation has been sent out.";

                }
            });
        }

    });


});


