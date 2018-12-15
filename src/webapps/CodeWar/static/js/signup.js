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
    $('#id_username').attr('placeholder', 'Username');

    $('#id_password1').attr('placeholder', 'Password');

    $('#id_password2').attr('placeholder', 'Password Confirm');

    $('#id_first_name').attr('placeholder', 'First Name');

    $('#id_last_name').attr('placeholder', 'Last Name');

    $('#id_age').attr('placeholder', 'Age');
    $('#id_bio').attr('placeholder', 'Bio');
    $('#id_email').attr('placeholder', 'Email');

});
