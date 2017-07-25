$.ajaxSetup( {

headers: { // 默认添加请求头
    "X-Frappe-CSRF-Token": "{{csrf_token}}",
    "Powered-By": "CodePlayer"
}
} );

function evcount_ref() {
    $.get("/api/method/iot_ui.ui_api.query_iot_event?filter=unread", function (r) {
        //console.log(r.message[0].device);
        events = r.message;
        if (events) {
            if (!(events[0].device == "No Data")) {
                $("#unread_mes1").text(events.length);
                $("#unread_mes2").text(events.length);
                $("#unread_mes3").text("+" + events.length);
            }
            else {
                $("#unread_mes1").text("");
                $("#unread_mes2").text("");
                $("#unread_mes3").text("");
            }

        }
        else{
            $("#unread_mes1").text("");
            $("#unread_mes2").text("");
            $("#unread_mes3").text("");
        }
    });
}


evcount_ref();
setInterval( function () {evcount_ref(); }, 3000 );

$('#switch_Language').click(function() {
//console.log("switch_Language");
//var userinfo = '{"first_name":"viccom","middle_name":"","last_name":"dong","user_image":{"__no_attachment":1},"phone":"","language":"en-US","doctype":"User","name":"viccom.dong@symid.com"}';
{% if language=="zh" %}
    var curlang = "en-US";
{% else %}
    var curlang = "zh";
{% endif %}
var userinfo = '{"language":"'+curlang+'","doctype":"User","name":"{{user}}"}';

var postdata = {
    "data":userinfo,
    "web_form":"edit-profile",
    "cmd":"frappe.website.doctype.web_form.web_form.accept"
};
//console.log(postdata);
$.ajax({
    type: 'POST',
    url: "/",
    contentType: "application/x-www-form-urlencoded", //必须有
    data: postdata,
    dataType: "json",
    success: function(r) {
            if(r.message){
                window.location.reload();
            }
      },
     error: function() {
          console.log("异常!");
      }
});
});