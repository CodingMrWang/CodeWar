var checkIntervalProcess = {};
var heartbeat_request;

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

    $.ajax({
        url: "/codewar/updateAllRooms",
        dataType: "json",
        headers: {
            "X-CSRFToken": csrftoken
        },
        type: 'POST',
        method: "POST",
        success: function (response) {
            updateRooms(response);
        }
    });


    $('body').on('click', '#create-room-button', function (event) {

        var room_type = $('#selected-room-type').val();

        var slogan = $('#slogan-content').val();
        var createRoomMeta = {
            "room_type": room_type,
            "slogan": slogan
        };
        $.ajax({
            url: "/createRoom",
            dataType: "json",
            headers: {
                "X-CSRFToken": csrftoken
            },
            data: createRoomMeta,
            type: 'POST',
            method: "POST"
        });
    });

    $(document).on('click', '.btn.btn-primary', function () {
        $('#createModal').appendTo("body").modal('show');
    });
    $(document).on('click', '.notification-envelop', function () {
        $('#invitationModal').appendTo("body").modal('show');
    });


    var heartbeat_invite = setInterval(function () {
        $.ajax({
            url: "/codewar/listenInvitation",
            dataType: "json",
            headers: {
                "X-CSRFToken": csrftoken
            },
            type: 'GET',
            method: "GET",
            success: function (response) {
                if (response['response'] === "exist") {
                    theList = response['invitation_list'];
                    for (var i = 0; i < theList.length; i++) {

                        updateInvitation(theList[i]);
                    }
                }
            }
        });
    }, 8000);


    $("#show-ranking").popover({
        placement: "right",
        html: "true",
        container: "body",
        title: "<span class=\"text-info\"><strong>The Ranking of Code War</strong></span><button type=\"button\" id=\"close\" class=\"close\" onclick=\"$(&quot;#show-ranking&quot;).popover(&quot;hide&quot;);\">&times;</button>",
        content: getRankings()
    });


    $("#user-profile").popover({

        placement: 'right',
        html: 'true',
        container: 'body',
        title: "<span class=\"text-info\"><strong>User Basic Information</strong></span><button type=\"button\" id=\"close\" class=\"close\" onclick=\"$(&quot;#user-profile&quot;).popover(&quot;hide&quot;);\">&times;</button>",
        content: getUserinfo()

    });

    function getUserinfo() {
        var userContent;
        $.ajax({
            url: "/codewar/getUserinfo",
            async: false,
            dataType: "json",
            headers: {"X-CSRFToken": csrftoken},
            type: 'GET',
            method: "GET",
            success: function (response) {
                userContent = "<div class=\"display_userinfo\"><div id='uid-pro'>Username: " + response['username'] + "</div>" + "<div id='win-pro'>FirstName: " + response['fname'] + "</div>" + "<div id='lname-pro'>LastName: " + response['lname'] + "</div>" + "<div id='win-pro'>Win: " + response['win'] + "</div>" +
                    "<div id='lose-pro'>Lose: " + response['lose'] + "</div>" + "<div id='bio-pro'>Description: " + response['bio'] + "</div>" + "</div>"

            }
        });
        return userContent;
    }

    function getRankings() {
        var loadedContent = "";
        $.ajax({
            url: "/codewar/getRankings",
            async: false,
            dataType: "json",
            headers: {"X-CSRFToken": csrftoken},
            type: 'GET',
            method: "GET",
            success: function (response) {
                loadedContent = loadRankings(response);

            }

        });

        return loadedContent;
    }

    function updateInvitation(response) {

        var invitor = response.invitor;
        var message = response.message;
        var room_id = response.room_id;
        var invitation_id = response.invitation_id;
        var photo_url = response.url;
        var newmessage = invitor + " -- " + message;
        var id_list = $('.invited_id_indicator');

        if (id_list.length === 0) {
            var footer = "<div class=\"modal-footer\">" +
                "<span style=\"padding-right:10%;\">" + newmessage +
                "</span>\n" +
                "<img class=\"invitation-user-profile\" src=\"/codewar" + photo_url + "\" style=\"margin-right:15px;\">" +
                "<input type=\"hidden\" name=\"invitation_id\" class=\"invited_id_indicator\" value='" + invitation_id + "'>\n" +
                "        <button type=\"button\" class=\"reject-btn\">Reject</button>\n" +
                "        <form id=\"accpetRoomfromothers\" action=\"/codewar/acceptRoom" +
                "\" method=\"post\">\n" +
                '<input name=\"csrfmiddlewaretoken\" value=\"' + csrftoken + '\" type=\"hidden\">' +
                "<input type=\"hidden\" name=\"room_id\" class=\"invited_room\" value='" + room_id + "'>\n" +
                "<button type=\"submit\" class=\"btn btn-primary\">Accept</button>\n" +
                "</form></div>";
            $('#message-div-indicator').after(footer);
            $('#invitationModal').find('#exampleModalLabel2')[0].innerHTML = "Some player invited you to join a game";
            $('#envelop-signal-svg').attr('src', '/codewar/media/envelop.svg');

        } else {
            for (var i = 0; i < id_list.length; i++) {
                var each = id_list[i];
                var each_val = each.value;
                if (invitation_id == id_list[i].value) {
                    return;
                }
                if (invitation_id != id_list[i].value) {
                    continue;
                }
            }
            var footer = "<div class=\"modal-footer\">" +
                "<span style=\"padding-right:10%;\">" + newmessage +
                "</span>\n" +
                "<img class=\"invitation-user-profile\" src=\"/codewar" + photo_url + "\" style=\"margin-right:15px;\">" +
                "<input type=\"hidden\" name=\"invitation_id\" class=\"invited_id_indicator\" value='" + invitation_id + "'>\n" +
                "        <button type=\"button\" class=\"reject-btn\">Reject</button>\n" +
                "        <form action=\"/codewar/acceptRoom\" method=\"post\">\n" +
                '<input name=\"csrfmiddlewaretoken\" value=\"' + csrftoken + '\" type=\"hidden\">' +
                "<input type=\"hidden\" name=\"room_id\" class=\"invited_room\" value='" + room_id + "'>\n" +
                "<button type=\"submit\" class=\"btn btn-primary\">Accept</button>\n" +
                "</form></div>";
            $('#message-div-indicator').after(footer);
            $('#invitationModal').find('#exampleModalLabel2')[0].innerHTML = "Some player invited you to join a game";
        }


    }

    $('body').on('click', '.reject-btn', function () {
        var to_delete_invitation = $(this).prev()[0].value;
        $(this).parent().remove();
        $.ajax({
            url: "/codewar/deleteInvitation",
            dataType: "json",
            headers: {
                "X-CSRFToken": csrftoken
            },
            data: {'invitation_id': to_delete_invitation},
            type: 'POST',
            method: "POST",
            success: function (response) {
                var id_list = $('.invited_id_indicator');
                if (id_list.length === 0) {
                    $('#invitationModal').find('#exampleModalLabel2')[0].innerHTML = "There is no pending invitation";
                    $('#envelop-signal-svg').attr('src', '/codewar/media/normal-envelop.svg');
                }

            }
        });

    });


    $('body').on('click', '.access-room', function (event) {
        var roomInfo = $(this).parent().parent().find('.text-dark')[0].innerHTML;

        if ($(this).parent().next()[0].src.includes('available')) {
            window.location.pathname = '/codewar/getInRoom/' + roomInfo + '/';
        }

    });

    function loadRankings(response) {
        var length = response.users.length;
        if (length > 10) {
            length = 10;
        }
        var return_content = "<div class=\"display_ranking\"><table class=\"the-result-table\">";
        for (var i = 0; i < length; i++) {

            var username = response.users[i]['username'];
            var winning_rate = response.users[i]['winning_rate'];
            var photo_url = response.users[i]['photo_url'];
            var bio = response.users[i]['des'];

            return_content += "<tr class=\"each-ranking-area\">\
<td><img class=\"ranking-user-profile\" onerror=\"this.src='/static/media/11539038077_.pic.jpg'\" src=\"/codewar" + photo_url + "\"></td>\
<td class=\"td-username\">" + username + "</td><td class=\"td-username\">" + winning_rate + "</td><td>" + bio + "</td></tr>"
        }
        return_content += "<table></div>";
        return return_content;
    }

    var heartbeat_request = setInterval(function () {
        $.ajax({
            url: "/codewar/updateAllRooms",
            dataType: "json",
            headers: {
                "X-CSRFToken": csrftoken
            },
            type: 'POST',
            method: "POST",
            success: function (response) {
                updateRooms(response);
            }
        });
    }, 8000);

    function updateRooms(data) {

        var page_int = Math.floor(data.rooms.length / 4);
        var rest = data.rooms.length - page_int * 4;

        $('#myCarousel').empty();


        var first_append_content = "<div class=\"item active\">";
        var rest_append_content = "<div class=\"item\">";
        var to_be_append = "<div class=\"carousel-inner\">";


        for (var i = 0; i < page_int; i++) {
            var prefix = "";

            if (i === 0) {
                prefix = first_append_content;
            } else {
                prefix = rest_append_content;
            }
            to_be_append += prefix +
                "<div class=\"row mb-2\">\
                  <div class=\"col-md-4\">\
                    <div class=\"card flex-md-row mb-4 shadow-sm h-md-250\">\
                      <div class=\"card-body d-flex flex-column align-items-start\">\
                        <h3 class=\"mb-0\">\
                          <a class=\"text-dark\" href=\"#\">Room " + data.rooms[i * 4].room_id + "</a>\
              </h3>\
              <div class=\"mb-1 text-muted\"></div>\
              <p class=\"card-text mb-auto\">" + data.rooms[i * 4].room_slogan + "</p>\
              <button type='submit' class=\"access-room\" > Get In Room</button>\
            </div>\
            <img class=\"card-img-right flex-auto d-none d-lg-block\" src=\"/codewar/media/" + data.rooms[i * 4].room_status + ".png\" alt=\"Card image cap\">\
          </div>\
        </div>\
         <div class=\"col-md-4\">\
          <div class=\"card flex-md-row mb-4 shadow-sm h-md-250\">\
            <div class=\"card-body d-flex flex-column align-items-start\">\
              <h3 class=\"mb-0\">\
                <a class=\"text-dark\" href=\"#\">Room " + data.rooms[i * 4 + 1].room_id + "</a>\
              </h3>\
              <div class=\"mb-1 text-muted\"></div>\
              <p class=\"card-text mb-auto\">" + data.rooms[i * 4 + 1].room_slogan + "</p>\
              <button type='submit' class=\"access-room\" > Get In Room </button>\
            </div>\
            <img class=\"card-img-right flex-auto d-none d-lg-block\" src=\"/codewar/media/" + data.rooms[i * 4 + 1].room_status + ".png\" alt=\"Card image cap\">\
          </div>\
        </div>\
    </div>\
  <div class=\"row mb-2\">\
        <div class=\"col-md-4\">\
          <div class=\"card flex-md-row mb-4 shadow-sm h-md-250\">\
            <div class=\"card-body d-flex flex-column align-items-start\">\
              <h3 class=\"mb-0\">\
                <a class=\"text-dark\" href=\"#\">Room " + data.rooms[i * 4 + 2].room_id + "</a>\
              </h3>\
              <div class=\"mb-1 text-muted\"></div>\
              <p class=\"card-text mb-auto\">" + data.rooms[i * 4 + 2].room_slogan + "</p>\
              <button type='submit' class=\"access-room\" > Get In Room </button>\
            </div>\
            <img class=\"card-img-right flex-auto d-none d-lg-block\" src=\"/codewar/media/" + data.rooms[i * 4 + 2].room_status + ".png\" alt=\"Card image cap\">\
          </div>\
        </div>\
         <div class=\"col-md-4\">\
          <div class=\"card flex-md-row mb-4 shadow-sm h-md-250\">\
            <div class=\"card-body d-flex flex-column align-items-start\">\
              <h3 class=\"mb-0\">\
                <a class=\"text-dark\" href=\"#\">Room " + data.rooms[i * 4 + 3].room_id + "</a>\
              </h3>\
              <div class=\"mb-1 text-muted\"></div>\
              <p class=\"card-text mb-auto\">" + data.rooms[i * 4 + 3].room_slogan + "</p>\
              <button type='submit' class=\"access-room\"> Get In Room</button>\
            </div>\
            <img class=\"card-img-right flex-auto d-none d-lg-block\" src=\"/codewar/media/" + data.rooms[i * 4 + 3].room_status + ".png\" alt=\"Card image cap\">\
          </div>\
        </div>\
    </div>\
    </div>";

        }
        var the_list = [];

        for (var i = 0; i < rest; i++) {
            the_list.push("nothing");
            the_list.push(data.rooms[data.rooms.length - i - 1].room_id);
            the_list.push(data.rooms[data.rooms.length - i - 1].room_slogan);
            the_list.push(data.rooms[data.rooms.length - i - 1].room_status);
        }
        var temp_length = the_list.length;
        for (var i = 0; i < ((12 - temp_length) / 4); i++) {
            the_list.push("display:none");
            the_list.push("display:none");
            the_list.push("display:none");
            the_list.push("display"); // just to prevent the 404 in getting photo in the undisplay html part...

        }

        var final_page_content = "";
        if (page_int === 0) {
            final_page_content += first_append_content;
        }
        else {
            final_page_content += rest_append_content;
        }
        final_page_content += "<div class=\"row mb-2\">\
        <div class=\"col-md-4\" style=" + the_list[0] + ">\
          <div class=\"card flex-md-row mb-4 shadow-sm h-md-250\">\
            <div class=\"card-body d-flex flex-column align-items-start\">\
              <h3 class=\"mb-0\">\
                <a class=\"text-dark\" href=\"#\">Room " + the_list[1] + "</a>\
              </h3>\
              <div class=\"mb-1 text-muted\"></div>\
              <p class=\"card-text mb-auto\">" + the_list[2] + "</p>\
              <button class=\"access-room\" > Get In Room</button>\
            </div>\
            <img class=\"card-img-right flex-auto d-none d-lg-block\" src=\"/codewar/media/" + the_list[3] + ".png\" alt=\"Card image cap\">\
          </div>\
        </div>\
         <div class=\"col-md-4\" style=" + the_list[4] + ">\
          <div class=\"card flex-md-row mb-4 shadow-sm h-md-250\">\
            <div class=\"card-body d-flex flex-column align-items-start\">\
              <h3 class=\"mb-0\">\
                <a class=\"text-dark\" href=\"#\">Room " + the_list[5] + "</a>\
              </h3>\
              <div class=\"mb-1 text-muted\"></div>\
              <p class=\"card-text mb-auto\">" + the_list[6] + "</p>\
              <button class=\"access-room\" > Get In Room </button>\
            </div>\
            <img class=\"card-img-right flex-auto d-none d-lg-block\" src=\"/codewar/media/" + the_list[7] + ".png\" alt=\"Card image cap\">\
          </div>\
        </div>\
    </div>\
  <div class=\"row mb-2\">\
        <div class=\"col-md-4\" style=" + the_list[8] + ">\
          <div class=\"card flex-md-row mb-4 shadow-sm h-md-250\">\
            <div class=\"card-body d-flex flex-column align-items-start\">\
              <h3 class=\"mb-0\">\
                <a class=\"text-dark\" href=\"#\">Room " + the_list[9] + "</a>\
              </h3>\
              <div class=\"mb-1 text-muted\"></div>\
              <p class=\"card-text mb-auto\">" + the_list[10] + "</p>\
              <button class=\"access-room\" > Get In Room </button>\
            </div>\
            <img class=\"card-img-right flex-auto d-none d-lg-block\" src=\"/codewar/media/" + the_list[11] + ".png\" alt=\"Card image cap\">\
          </div>\
        </div>\
         <div class=\"col-md-4\" style=\"display:none;\">\
          <div class=\"card flex-md-row mb-4 shadow-sm h-md-250\">\
            <div class=\"card-body d-flex flex-column align-items-start\">\
              <h3 class=\"mb-0\">\
                <a class=\"text-dark\" href=\"#\">Room </a>\
              </h3>\
              <div class=\"mb-1 text-muted\"></div>\
              <p class=\"card-text mb-auto\"></p>\
              <button class=\"access-room\"> Get In Room</button>\
            </div>\
            <img class=\"card-img-right flex-auto d-none d-lg-block\" src=\"/codewar/media/available.png\" alt=\"Card image cap\">\
          </div>\
        </div>\
    </div></div></div></div>";

        to_be_append += final_page_content;
        var control = "<a class=\"left carousel-control\" href=\"#myCarousel\" data-slide=\"prev\">\
    <span class=\"glyphicon glyphicon-chevron-left\"></span>\
    <span class=\"sr-only\">Previous</span>\
  </a>\
  <a class=\"right carousel-control\" href=\"#myCarousel\" data-slide=\"next\">\
    <span class=\"glyphicon glyphicon-chevron-right\"></span>\
    <span class=\"sr-only\">Next</span>\
  </a>";
        to_be_append += control;

        $('#myCarousel').append(to_be_append);

    }


});
